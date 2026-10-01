#!/usr/bin/env python3
"""Export ComfyUI API workflows and download selected template models."""

import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from urllib.parse import urlparse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "templates_models.db"
DOWNLOADER = BASE_DIR / "comfy_model_downloader.sh"
DEFAULT_COMFY_DIR = Path("/workspace/ComfyUI") if Path("/workspace").is_dir() else BASE_DIR / "ComfyUI"
COMFY_DIR = Path(os.environ.get("COMFY_DIR", DEFAULT_COMFY_DIR))
EXPORT_DIR = Path(os.environ.get("COMFY_TEMPLATE_EXPORT_DIR", COMFY_DIR / "template_apis"))


def template_ids(raw):
    values = [part.strip() for part in raw.split(",")]
    if not values or any(not value.isdecimal() or int(value) < 1 for value in values):
        raise ValueError("Укажите ID шаблонов через запятую, например: 89,93,94")
    return list(dict.fromkeys(map(int, values)))


def load_templates(ids):
    if not DB_PATH.is_file():
        raise ValueError(f"База шаблонов не найдена: {DB_PATH}")
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"SELECT id, name, api_json, workflow_json FROM templates "
            f"WHERE id IN ({','.join('?' for _ in ids)})", ids
        ).fetchall()
        by_id = {row["id"]: row for row in rows}
        missing = [number for number in ids if number not in by_id]
        if missing:
            raise ValueError(f"Неизвестные ID шаблонов: {', '.join(map(str, missing))}")
        result = []
        for number in ids:
            row = by_id[number]
            models = connection.execute(
                "SELECT name, directory, url FROM models WHERE template_id = ? ORDER BY id",
                (number,),
            ).fetchall()
            result.append((row, models))
        return result


def validate_model(row):
    name, directory, url = row["name"], row["directory"], row["url"]
    if name in ("", ".", "..") or Path(name).name != name:
        raise ValueError(f"Недопустимое имя модели: {name!r}")
    if directory in ("", ".", "..") or Path(directory).name != directory:
        raise ValueError(f"Недопустимая папка модели: {directory!r}")
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise ValueError(f"Недопустимый URL модели: {url!r}")


def prepare(selected):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    downloads = {}
    for template, models in selected:
        number = template["id"]
        api = json.loads(template["api_json"])
        api_file = EXPORT_DIR / f"{number}.api.json"
        api_file.write_text(json.dumps(api, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        workflow_file = None
        if template["workflow_json"]:
            workflow = json.loads(template["workflow_json"])
            workflow_file = EXPORT_DIR / f"{number}.workflow.json"
            workflow_file.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for model in models:
            validate_model(model)
            key = (model["directory"], model["name"])
            if key in downloads and downloads[key] != model["url"]:
                print(f"Общий файл models/{key[0]}/{key[1]} указан с разными URL; используется первый", flush=True)
            else:
                downloads.setdefault(key, model["url"])
        manifest.append({
            "id": number,
            "name": template["name"],
            "api_json": str(api_file),
            "workflow_json": str(workflow_file) if workflow_file else None,
            "models": [f"models/{m['directory']}/{m['name']}" for m in models],
            "node_types": sorted({
                node["class_type"] for node in api.values()
                if isinstance(node, dict) and isinstance(node.get("class_type"), str)
            }) if isinstance(api, dict) else [],
        })
    (EXPORT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return downloads, manifest


def download_one(item):
    (directory, name), url = item
    target = COMFY_DIR / "models" / directory / name
    if target.is_file() and target.stat().st_size > 0:
        print(f"Пропущено: {target}", flush=True)
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["bash", str(DOWNLOADER), "--download", url,
           "--folder", directory, "--filename", name, "--yes"]
    print(f"Загрузка: models/{directory}/{name}", flush=True)
    completed = subprocess.run(cmd, env=os.environ.copy(), check=False)
    if completed.returncode != 0 and not (target.is_file() and target.stat().st_size > 0):
        print(f"Ошибка загрузки: models/{directory}/{name}, код {completed.returncode}", flush=True)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("list", "validate", "prepare", "download"))
    parser.add_argument("--templates", default="")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    if args.action == "list":
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as connection:
            for number, name, count in connection.execute(
                "SELECT id, name, model_count FROM templates ORDER BY id"
            ):
                print(f"{number:3}  {name}  ({count} моделей)")
        return 0
    if not 1 <= args.workers <= 4:
        parser.error("--workers должен быть от 1 до 4")
    try:
        selected = load_templates(template_ids(args.templates))
        if args.action == "validate":
            print("Выбраны шаблоны: " + ", ".join(
                f"{template['id']} ({template['name']})" for template, _ in selected
            ))
            return 0
        downloads, manifest = prepare(selected)
    except (ValueError, sqlite3.Error, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"API JSON готовы в {EXPORT_DIR}; шаблонов: {len(manifest)}, уникальных моделей: {len(downloads)}", flush=True)
    if args.action == "prepare":
        return 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(download_one, downloads.items()))
    failed = results.count(False)
    print(f"Загрузка завершена: {len(results) - failed} успешно, {failed} ошибок", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
