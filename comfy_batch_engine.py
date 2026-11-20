#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Headless ComfyUI batch prompt engine (no GUI dependencies).

Shared core extracted from comfy_prompt_batcher for server-side execution
inside comfy_control_panel.py and reuse by CLI/desktop clients.
"""

from collections import deque
import copy
import datetime
import json
import os
from pathlib import Path
import random
import re
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid


MAX_CONSECUTIVE_FAILURES = 3
PROMPT_KEYWORDS = (
    "masterpiece", "detailed", "quality", "photorealistic", "beautiful",
    "highres", "highly", "portrait", "scenery", "background", "embedding:",
)
SYSTEM_KEYWORDS = (
    "you are an expert", "your task is", "system prompt", "instruction",
    "template", "user's input", "follow these rules", "think step by step",
)
NON_PROMPT_EXTENSIONS = (
    ".safetensors", ".ckpt", ".pt", ".png", ".jpg", ".jpeg", ".webp",
    ".yaml", ".json", ".txt", ".mp4", ".bin",
)
SEED_INPUT_KEYS = ("seed", "noise_seed")


def clean_server_url(raw_url):
    """Normalize a ComfyUI server URL (strip whitespace, query, fragment, trailing slash)."""
    if not raw_url:
        return ""
    return raw_url.strip().split("#")[0].split("?")[0].rstrip("/")


def sanitize_folder_name(name):
    if not name:
        return "unknown_model"
    cleaned = "".join(c for c in name if c.isalnum() or c in ("-", "_", ".", " ")).strip()
    cleaned = cleaned.replace(" ", "_")
    return cleaned or "unknown_model"


def extract_model_name(workflow_data):
    """Return the primary model filename stem referenced by an API workflow."""
    if not isinstance(workflow_data, dict):
        return None
    priority_keys = ("ckpt_name", "unet_name", "model_name", "clip_name", "vae_name")
    found_inputs = {key: [] for key in priority_keys}
    for node_spec in workflow_data.values():
        if not isinstance(node_spec, dict):
            continue
        inputs = node_spec.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        for key in priority_keys:
            value = inputs.get(key)
            if isinstance(value, str) and value.strip():
                found_inputs[key].append(value.strip())
    for key in priority_keys:
        if found_inputs[key]:
            val = os.path.basename(found_inputs[key][0])
            base, _ = os.path.splitext(val)
            return base
    return None


def format_filename(pattern, original_filename, prompt_text, prompt_id, index, workflow_name):
    if not pattern or pattern == "{original}":
        return original_filename

    orig_base, ext = os.path.splitext(original_filename)
    index_str = f"{index + 1:03d}"
    short_id = prompt_id[:8] if prompt_id else "unknown"
    dt_str = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    new_name = pattern
    new_name = new_name.replace("{original}", orig_base)
    new_name = new_name.replace("{index}", index_str)
    new_name = new_name.replace("{prompt_id}", short_id)
    new_name = new_name.replace("{datetime}", dt_str)
    new_name = new_name.replace("{workflow}", workflow_name or "workflow")

    if "{prompt_all}" in new_name or "{prompt}" in new_name:
        words = "".join(c for c in prompt_text if c.isalnum() or c.isspace()).lower().split()
        prompt_clean = "_".join(words) or "prompt"
        new_name = new_name.replace("{prompt_all}", prompt_clean).replace("{prompt}", prompt_clean)

    matches = re.findall(r"\{prompt_(\d+)\}", new_name)
    if matches:
        words = "".join(c for c in prompt_text if c.isalnum() or c.isspace()).lower().split()
        for num_str in matches:
            num = int(num_str)
            prompt_clean_n = "_".join(words[:num]) or "prompt"
            new_name = new_name.replace(f"{{prompt_{num_str}}}", prompt_clean_n)

    new_name = "".join(c for c in new_name if c not in ("/", "\\", ":", "*", "?", '"', "<", ">", "|"))
    return new_name + ext


def detect_prompt_nodes(workflow_data):
    """Score and rank string input fields in an API workflow to locate the prompt node.

    Returns a list of dicts sorted by descending heuristic score:
    ``{"node_id", "input_key", "class_type", "score", "label", "value"}``
    where ``value`` is ``f"{node_id}::{input_key}"``.
    """
    if not isinstance(workflow_data, dict):
        return []

    candidates = []
    for node_id, node_spec in workflow_data.items():
        if not isinstance(node_spec, dict):
            continue
        inputs = node_spec.get("inputs", {})
        if not isinstance(inputs, dict):
            continue
        class_type = str(node_spec.get("class_type", "UnknownNode"))

        for input_key, input_val in inputs.items():
            if not isinstance(input_val, str):
                continue

            score = 0
            if class_type == "CLIPTextEncode" and input_key == "text":
                score += 150
            elif "CLIPText" in class_type or "Prompt" in class_type or "TextToImage" in class_type:
                score += 80

            if input_key in ("text", "prompt", "text_g", "text_l", "positive"):
                score += 50
            elif input_key in ("negative", "text_w"):
                score -= 30

            val_len = len(input_val)
            score += min(val_len, 150)
            score += min(len(input_val.split()) * 5, 100)
            score += min(input_val.count(",") * 15, 120)

            lower_val = input_val.lower()
            for kw in PROMPT_KEYWORDS:
                if kw in lower_val:
                    score += 15
            for skw in SYSTEM_KEYWORDS:
                if skw in lower_val:
                    score -= 300

            if any(lower_val.endswith(ext) for ext in NON_PROMPT_EXTENSIONS):
                score -= 300

            try:
                float(input_val.strip())
                score -= 200
            except ValueError:
                pass

            if " " not in input_val.strip() and "," not in input_val and val_len < 20:
                score -= 100

            truncated = (input_val[:30] + "...") if len(input_val) > 30 else input_val
            base_label = f"[{node_id}] {class_type} -> {input_key} (\"{truncated}\")"
            candidates.append({
                "node_id": str(node_id),
                "input_key": str(input_key),
                "class_type": class_type,
                "score": score,
                "label": base_label,
                "value": f"{node_id}::{input_key}",
            })

    candidates.sort(key=lambda item: item["score"], reverse=True)
    if candidates and candidates[0]["score"] > 0:
        candidates[0]["label"] = "⭐ " + candidates[0]["label"] + " (Авто)"
    return candidates


def parse_node_selection(selection):
    """Split a ``node_id::input_key`` selector into ``(node_id, input_key)``."""
    if not selection or "::" not in selection:
        return None, None
    node_id, input_key = selection.split("::", 1)
    return node_id, input_key


def parse_prompts_text(raw_text):
    """Extract non-empty prompt lines from raw multiline text."""
    if not raw_text:
        return []
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def randomize_workflow_seeds(workflow_data, rng=None):
    """Randomize integer seed/noise_seed inputs in place; returns count updated."""
    if not isinstance(workflow_data, dict):
        return 0
    generator = rng or random
    updated = 0
    for node_spec in workflow_data.values():
        if not isinstance(node_spec, dict):
            continue
        inputs = node_spec.get("inputs")
        if not isinstance(inputs, dict):
            continue
        for key in SEED_INPUT_KEYS:
            value = inputs.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                inputs[key] = generator.randint(1, (1 << 53) - 1)
                updated += 1
    return updated


def apply_filename_prefix(workflow_data, prefix):
    """Set filename_prefix on SaveImage/SaveVideo nodes when requested."""
    if not prefix or not isinstance(workflow_data, dict):
        return 0
    updated = 0
    for node_spec in workflow_data.values():
        if not isinstance(node_spec, dict):
            continue
        inputs = node_spec.get("inputs")
        if isinstance(inputs, dict) and isinstance(inputs.get("filename_prefix"), str):
            inputs["filename_prefix"] = prefix
            updated += 1
    return updated


def _http_json(url, payload=None, timeout=15):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    request = Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, json.loads(body) if body.strip() else {}


def _extract_output_files(history_entry, output_dir=None):
    """Extract generated image/media file paths from a ComfyUI /history entry."""
    found = []
    outputs = history_entry.get("outputs", {}) if isinstance(history_entry, dict) else {}
    if not isinstance(outputs, dict):
        return found
    for node_output in outputs.values():
        if not isinstance(node_output, dict):
            continue
        for media_key in ("images", "gifs", "videos"):
            items = node_output.get(media_key, [])
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict) or not item.get("filename"):
                    continue
                if item.get("type", "output") != "output":
                    continue
                subfolder = item.get("subfolder", "")
                filename = item["filename"]
                if output_dir:
                    candidate = Path(output_dir) / subfolder / filename if subfolder else Path(output_dir) / filename
                    found.append(str(candidate))
                else:
                    found.append(os.path.join(subfolder, filename) if subfolder else filename)
    return found


class BatchRunner:
    """Thread-safe server-side batch prompt runner talking directly to ComfyUI HTTP API."""

    def __init__(self, poll_interval=0.8):
        self.poll_interval = poll_interval
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread = None
        self._state = self._empty_state()

    @staticmethod
    def _empty_state():
        return {
            "running": False,
            "stop_requested": False,
            "total": 0,
            "completed": 0,
            "succeeded": 0,
            "failed": 0,
            "current_index": -1,
            "started_at": 0.0,
            "finished_at": 0.0,
            "last_image": None,
            "last_prompt": "",
            "summary": "Готов к запуску пакетной генерации.",
            "rows": [],
            "logs": deque(maxlen=500),
            "server_url": "",
        }

    def _log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        with self._lock:
            self._state["logs"].append(f"[{timestamp}] {message}")

    def _set_row(self, index, status, details):
        with self._lock:
            if 0 <= index < len(self._state["rows"]):
                self._state["rows"][index][1] = status
                self._state["rows"][index][3] = details

    def is_running(self):
        with self._lock:
            return self._state["running"]

    def snapshot(self):
        with self._lock:
            return {
                "running": self._state["running"],
                "stop_requested": self._state["stop_requested"],
                "total": self._state["total"],
                "completed": self._state["completed"],
                "succeeded": self._state["succeeded"],
                "failed": self._state["failed"],
                "current_index": self._state["current_index"],
                "started_at": self._state["started_at"],
                "finished_at": self._state["finished_at"],
                "last_image": self._state["last_image"],
                "last_prompt": self._state["last_prompt"],
                "summary": self._state["summary"],
                "rows": [list(row) for row in self._state["rows"]],
                "logs": "\n".join(self._state["logs"]),
            }

    def start(
        self,
        server_url,
        workflow_data,
        node_id,
        input_key,
        prompts,
        *,
        sequential=True,
        randomize_seeds=True,
        filename_prefix="",
        output_dir=None,
    ):
        clean_url = clean_server_url(server_url)
        if not clean_url:
            return False, "Не указан URL сервера ComfyUI."
        if not isinstance(workflow_data, dict) or not workflow_data:
            return False, "Workflow JSON не загружен или пуст."
        node_spec = workflow_data.get(node_id)
        if not isinstance(node_spec, dict) or input_key not in node_spec.get("inputs", {}):
            return False, f"Узел [{node_id}] с полем '{input_key}' не найден в workflow."
        cleaned_prompts = [p.strip() for p in prompts if p and p.strip()]
        if not cleaned_prompts:
            return False, "Список промптов пуст."

        with self._lock:
            if self._state["running"]:
                return False, "Пакетная генерация уже выполняется."
            self._stop_event.clear()
            self._state = self._empty_state()
            self._state.update({
                "running": True,
                "total": len(cleaned_prompts),
                "started_at": time.time(),
                "summary": f"Запуск пакетной генерации: 0/{len(cleaned_prompts)}...",
                "server_url": clean_url,
                "rows": [
                    [
                        idx + 1,
                        "⏳ В очереди",
                        (text[:80] + "…") if len(text) > 80 else text,
                        "",
                    ]
                    for idx, text in enumerate(cleaned_prompts)
                ],
            })

        worker = threading.Thread(
            target=self._run_loop,
            args=(
                clean_url,
                copy.deepcopy(workflow_data),
                node_id,
                input_key,
                cleaned_prompts,
                bool(sequential),
                bool(randomize_seeds),
                (filename_prefix or "").strip(),
                output_dir,
            ),
            daemon=True,
        )
        self._thread = worker
        worker.start()
        return True, f"Запущено {len(cleaned_prompts)} промптов."

    def stop(self, interrupt_server=False):
        with self._lock:
            if not self._state["running"]:
                return "Нет активной пакетной генерации."
            self._state["stop_requested"] = True
            server_url = self._state["server_url"]
        self._stop_event.set()
        self._log("Запрошена остановка пакетной генерации...")
        if interrupt_server and server_url:
            try:
                _http_json(f"{server_url}/interrupt", payload={}, timeout=5)
                self._log("Отправлена команда прерывания текущей генерации (/interrupt).")
            except (HTTPError, URLError, OSError, ValueError) as exc:
                self._log(f"Не удалось отправить /interrupt: {exc}")
        return "Остановка запрошена; новые промпты отправляться не будут."

    def _wait_for_prompt(self, server_url, prompt_id):
        """Poll ComfyUI /history/{prompt_id} until finished or stopped."""
        history_url = f"{server_url}/history/{prompt_id}"
        queue_url = f"{server_url}/queue"
        checks = 0
        while not self._stop_event.is_set():
            try:
                _, data = _http_json(history_url, timeout=10)
                if isinstance(data, dict) and prompt_id in data:
                    return data[prompt_id], None
            except (HTTPError, URLError, OSError, ValueError) as exc:
                return None, f"Ошибка опроса /history: {exc}"

            checks += 1
            # Every ~5 polls, verify prompt wasn't cancelled/dropped from queue.
            if checks % 5 == 0:
                try:
                    _, qdata = _http_json(queue_url, timeout=10)
                    running_ids = {item[1] for item in qdata.get("queue_running", []) if len(item) > 1}
                    pending_ids = {item[1] for item in qdata.get("queue_pending", []) if len(item) > 1}
                    if prompt_id not in running_ids and prompt_id not in pending_ids:
                        _, data = _http_json(history_url, timeout=10)
                        if isinstance(data, dict) and prompt_id in data:
                            return data[prompt_id], None
                        return None, "Задание исчезло из очереди ComfyUI (возможно, прервано)."
                except (HTTPError, URLError, OSError, ValueError):
                    pass

            self._stop_event.wait(self.poll_interval)
        return None, "Остановлено пользователем"

    def _run_loop(
        self,
        server_url,
        workflow_data,
        node_id,
        input_key,
        prompts,
        sequential,
        randomize_seeds,
        filename_prefix,
        output_dir,
    ):
        client_id = str(uuid.uuid4())
        prompt_url = f"{server_url}/prompt"
        total = len(prompts)
        consecutive_failures = 0
        mode_label = "последовательный" if sequential else "быстрая очередь"
        self._log(f"Старт батча: {total} промптов -> {prompt_url} (режим: {mode_label})")

        try:
            for idx, prompt_text in enumerate(prompts):
                if self._stop_event.is_set():
                    self._set_row(idx, "⏹️ Отменено", "Остановлено пользователем")
                    continue

                with self._lock:
                    self._state["current_index"] = idx
                    self._state["summary"] = (
                        f"Выполняется {idx + 1}/{total} "
                        f"(готово: {self._state['succeeded']}, ошибок: {self._state['failed']})"
                    )

                self._set_row(idx, "🚀 Отправка", "Подготовка workflow...")
                local_wf = copy.deepcopy(workflow_data)
                local_wf[node_id]["inputs"][input_key] = prompt_text
                if randomize_seeds:
                    randomize_workflow_seeds(local_wf)
                if filename_prefix:
                    apply_filename_prefix(local_wf, filename_prefix)

                try:
                    status_code, response_json = _http_json(
                        prompt_url,
                        payload={"prompt": local_wf, "client_id": client_id},
                        timeout=15,
                    )
                except (HTTPError, URLError, OSError, ValueError) as exc:
                    consecutive_failures += 1
                    self._set_row(idx, "❌ Ошибка", str(exc)[:120])
                    self._log(f"[{idx + 1}/{total}] Ошибка отправки: {exc}")
                    with self._lock:
                        self._state["completed"] += 1
                        self._state["failed"] += 1
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        self._log("Превышен лимит последовательных ошибок — батч остановлен.")
                        break
                    continue

                prompt_id = response_json.get("prompt_id") if isinstance(response_json, dict) else None
                if status_code != 200 or not prompt_id:
                    consecutive_failures += 1
                    err_detail = f"HTTP {status_code}: нет prompt_id"
                    self._set_row(idx, "❌ Ошибка", err_detail)
                    self._log(f"[{idx + 1}/{total}] {err_detail}")
                    with self._lock:
                        self._state["completed"] += 1
                        self._state["failed"] += 1
                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        self._log("Превышен лимит последовательных ошибок — батч остановлен.")
                        break
                    continue

                consecutive_failures = 0
                short_id = prompt_id[:8]
                self._log(f"[{idx + 1}/{total}] В очереди ({short_id}): {prompt_text[:60]}")

                if not sequential:
                    self._set_row(idx, "✅ В очереди ComfyUI", f"ID: {short_id}")
                    with self._lock:
                        self._state["completed"] += 1
                        self._state["succeeded"] += 1
                    continue

                self._set_row(idx, "⚙️ Генерация", f"ID: {short_id}")
                history_entry, wait_err = self._wait_for_prompt(server_url, prompt_id)
                if wait_err:
                    label = "⏹️ Остановлено" if self._stop_event.is_set() else "❌ Ошибка"
                    self._set_row(idx, label, wait_err)
                    self._log(f"[{idx + 1}/{total}] {wait_err}")
                    with self._lock:
                        self._state["completed"] += 1
                        if not self._stop_event.is_set():
                            self._state["failed"] += 1
                    continue

                status_info = history_entry.get("status", {}) if isinstance(history_entry, dict) else {}
                if status_info.get("status_str") == "error":
                    self._set_row(idx, "❌ Ошибка ComfyUI", f"ID: {short_id}")
                    self._log(f"[{idx + 1}/{total}] ComfyUI вернул ошибку для {short_id}")
                    with self._lock:
                        self._state["completed"] += 1
                        self._state["failed"] += 1
                    continue

                files = _extract_output_files(history_entry, output_dir=output_dir)
                image_preview = None
                for path in files:
                    if os.path.isfile(path) and path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        image_preview = path
                details = os.path.basename(files[-1]) if files else f"ID: {short_id}"
                self._set_row(idx, "✅ Готово", details)
                self._log(f"[{idx + 1}/{total}] Готово -> {details}")
                with self._lock:
                    self._state["completed"] += 1
                    self._state["succeeded"] += 1
                    if image_preview:
                        self._state["last_image"] = image_preview
                        self._state["last_prompt"] = prompt_text
        finally:
            with self._lock:
                self._state["running"] = False
                self._state["finished_at"] = time.time()
                stopped = self._state["stop_requested"]
                succ = self._state["succeeded"]
                fail = self._state["failed"]
                if stopped:
                    self._state["summary"] = f"⏹️ Остановлено: успешно {succ}/{total}, ошибок: {fail}"
                else:
                    self._state["summary"] = f"✅ Завершено: успешно {succ}/{total}, ошибок: {fail}"
            self._log(self._state["summary"])
