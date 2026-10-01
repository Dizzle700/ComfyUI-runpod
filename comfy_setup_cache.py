#!/usr/bin/env python3
"""Validate a completed RunPod installation before skipping pip on restart."""

import argparse
import hashlib
import importlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import tempfile


SCHEMA_VERSION = 1
REQUIRED_IMPORTS = (
    "torch", "gradio", "fastapi", "uvicorn", "psutil", "tiktoken",
    "sentencepiece", "google.protobuf", "transformers", "huggingface_hub",
    "hf_xet", "chardet", "safetensors", "numpy", "PIL", "aiohttp", "yaml",
)


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def requirement_files(path):
    """Include local -r/-c files so editing nested dependencies invalidates cache."""
    hashes = {}

    def visit(current):
        current = current.resolve()
        if str(current) in hashes:
            return
        hashes[str(current)] = file_hash(current)
        if not current.is_file():
            return
        text = current.read_text(encoding="utf-8").replace("\\\n", "")
        for line in text.splitlines():
            if not line.lstrip().startswith(("-r", "-c", "--requirement", "--constraint")):
                continue
            fields = shlex.split(line, comments=True)
            if not fields:
                continue
            option = fields[0]
            included = None
            if option in ("-r", "-c", "--requirement", "--constraint") and len(fields) > 1:
                included = fields[1]
            elif option.startswith(("--requirement=", "--constraint=")):
                included = option.split("=", 1)[1]
            elif option.startswith(("-r", "-c")) and len(option) > 2:
                included = option[2:]
            if included and "://" not in included:
                visit(current.parent / included)

    visit(path)
    return hashes


def repo_commit(path):
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def installation_inputs(comfy_dir, script_dir):
    manager_dir = comfy_dir / "custom_nodes" / "comfyui-manager"
    return {
        "comfy_commit": repo_commit(comfy_dir),
        "manager_commit": repo_commit(manager_dir),
        "files": {
            "comfy_requirements": requirement_files(comfy_dir / "requirements.txt"),
            "manager_requirements": requirement_files(manager_dir / "requirements.txt"),
            "panel_requirements": requirement_files(script_dir / "requirements.txt"),
            "torch_constraints": file_hash(comfy_dir / ".runpod-torch-constraints.txt"),
            "installer": file_hash(script_dir / "comfy_install_runpod.sh"),
            "cache_helper": file_hash(Path(__file__).resolve()),
        },
    }


def python_environment():
    return {
        "executable": os.path.realpath(sys.executable),
        "prefix": os.path.realpath(sys.prefix),
        "version": sys.version,
        "machine": platform.machine(),
    }


def installed_packages():
    packages = {}
    for distribution in metadata.distributions():
        name = distribution.metadata.get("Name")
        if name:
            normalized = name.lower().replace("_", "-").replace(".", "-")
            packages.setdefault(normalized, []).append({
                "version": distribution.version,
                "location": os.path.realpath(distribution.locate_file("")),
            })
    return {
        name: sorted(values, key=lambda item: (item["location"], item["version"]))
        for name, values in packages.items()
    }


def check_imports():
    for name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(name)
        except Exception as exc:
            raise RuntimeError(f"Пакет {name} не импортируется: {exc}") from exc


def check_cache(stamp, comfy_dir, script_dir):
    try:
        saved = json.loads(stamp.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "Нет действующей отметки завершённой установки."
    if not isinstance(saved, dict) or saved.get("schema") != SCHEMA_VERSION:
        return False, "Формат отметки установки изменился."
    if saved.get("inputs") != installation_inputs(comfy_dir, script_dir):
        return False, "Изменились репозитории, requirements или правила установки."
    if saved.get("python") != python_environment():
        return False, "Изменилось Python-окружение."
    previous = saved.get("packages")
    if not isinstance(previous, dict) or not previous:
        return False, "В отметке нет списка установленных пакетов."
    current = installed_packages()
    if "hf-gradio" in current:
        return False, "Обнаружен несовместимый hf-gradio; нужна проверка зависимостей."
    # Дополнительные пакеты custom nodes сами по себе не требуют переустановки.
    for name, version_info in previous.items():
        if current.get(name) != version_info:
            return False, f"Пакет {name} удалён или изменился."
    try:
        check_imports()
    except RuntimeError as exc:
        return False, str(exc)
    return True, "Версии и зависимости проверены; pip install пропускаем."


def save_cache(stamp, comfy_dir, script_dir):
    # Проверка выполняется до записи: не отмечаем сломанную установку как готовую.
    check_imports()
    contents = {
        "schema": SCHEMA_VERSION,
        "inputs": installation_inputs(comfy_dir, script_dir),
        "python": python_environment(),
        "packages": installed_packages(),
    }
    stamp.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=stamp.parent,
            prefix=stamp.name + ".", delete=False,
        ) as stream:
            temp_name = stream.name
            json.dump(contents, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, stamp)
    finally:
        if temp_name is not None and os.path.exists(temp_name):
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "save"))
    parser.add_argument("--comfy-dir", type=Path, required=True)
    parser.add_argument("--script-dir", type=Path, required=True)
    args = parser.parse_args()
    stamp = args.comfy_dir / ".runpod-setup.json"
    try:
        if args.action == "save":
            save_cache(stamp, args.comfy_dir, args.script_dir)
            print(f"Отметка завершённой установки сохранена: {stamp}")
            return 0
        ready, reason = check_cache(stamp, args.comfy_dir, args.script_dir)
        print(reason, flush=True)
        return 0 if ready else 1
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Проверка установки: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
