#!/usr/bin/env bash

set -Eeuo pipefail

# Определяем директорию, в которой находится этот скрипт.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SECRET_ENV_FILE="${COMFY_SECRET_FILE:-$SCRIPT_DIR/.env.secrets}"
MODEL_PACKAGES=''
TEMPLATE_IDS=''
export COMFY_UPDATE_ON_START="${COMFY_UPDATE_ON_START:-0}"
export COMFY_FORCE_INSTALL="${COMFY_FORCE_INSTALL:-0}"

usage() {
    cat <<'EOF'
Использование:
  runpod_startup.sh [--models ИМЯ_ПАКЕТА]... [--templates ID[,ID]...]

Опции:
  --models ИМЯ       Скачать модели из пакета #ИМЯ в KRea.txt до запуска
                      панели. Несколько имен укажите через запятую или
                      повторите опцию.
  --templates ID      Экспортировать API JSON шаблонов из SQLite и скачать
                      их модели в фоне параллельно запуску ComfyUI. ID через запятую.
  --update            Обновить ComfyUI и Manager, проверить зависимости через pip.
  --reinstall         Принудительно выполнить pip install без обновления Git.
  --help, -h          Показать эту справку.

Пример:
  runpod_startup.sh --templates 89,93,94
EOF
}

add_model_package() {
    local package
    local -a packages
    local IFS=','

    read -r -a packages <<< "$1"
    for package in "${packages[@]}"; do
        if [[ ! "$package" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
            echo "Ошибка: недопустимое имя пакета моделей: $package" >&2
            exit 2
        fi
        if [[ -n "$MODEL_PACKAGES" ]]; then
            MODEL_PACKAGES+=","
        fi
        MODEL_PACKAGES+="$package"
    done
}

add_template_ids() {
    local value=$1 id
    local -a ids
    IFS=',' read -r -a ids <<< "$value"
    [[ -n "$value" && "$value" != ,* && "$value" != *, && "$value" != *,,* ]] || {
        echo "Ошибка: укажите ID шаблонов через запятую." >&2
        exit 2
    }
    for id in "${ids[@]}"; do
        [[ "$id" =~ ^[1-9][0-9]*$ ]] || { echo "Недопустимый ID шаблона: $id" >&2; exit 2; }
        [[ -z "$TEMPLATE_IDS" ]] || TEMPLATE_IDS+=,
        TEMPLATE_IDS+="$id"
    done
}

# RunPod template environment variables use the same validation as CLI flags.
[[ -z "${COMFY_MODEL_PACKAGES:-}" ]] || add_model_package "$COMFY_MODEL_PACKAGES"
[[ -z "${COMFY_TEMPLATE_IDS:-}" ]] || add_template_ids "$COMFY_TEMPLATE_IDS"

while (( $# > 0 )); do
    case "$1" in
        --models)
            if (( $# < 2 )); then
                echo "Ошибка: после --models укажите имя пакета." >&2
                exit 2
            fi
            add_model_package "$2"
            shift
            ;;
        --models=*) add_model_package "${1#--models=}" ;;
        --templates)
            if (( $# < 2 )); then
                echo "Ошибка: после --templates укажите ID." >&2
                exit 2
            fi
            add_template_ids "$2"
            shift
            ;;
        --templates=*) add_template_ids "${1#--templates=}" ;;
        --update) export COMFY_UPDATE_ON_START=1 ;;
        --reinstall) export COMFY_FORCE_INSTALL=1 ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Ошибка: неизвестная опция: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

export COMFY_MODEL_PACKAGES="$MODEL_PACKAGES"
export COMFY_TEMPLATE_IDS="$TEMPLATE_IDS"

if [[ -n "$TEMPLATE_IDS" && "${COMFY_PREBUILT:-0}" != 1 ]]; then
    python3 "$SCRIPT_DIR/comfy_template_startup.py" validate --templates "$TEMPLATE_IDS"
fi

load_secret_file() {
    local key value
    [[ -f "$SECRET_ENV_FILE" ]] || return 0
    chmod 600 "$SECRET_ENV_FILE"

    # Безопасно разбираем только известные KEY=VALUE, не исполняя содержимое файла.
    while IFS= read -r -d '' key && IFS= read -r -d '' value; do
        if [[ -z "${!key:-}" ]]; then
            printf -v "$key" '%s' "$value"
            export "$key"
        fi
    done < <(python3 - "$SECRET_ENV_FILE" <<'PY'
import shlex
import sys

allowed = {
    "PANEL_USER", "PANEL_PASS", "HF_TOKEN", "CIVITAI_API_TOKEN",
    "NANO_BANANA_API_KEY", "FAL_KEY",
}
with open(sys.argv[1], encoding="utf-8") as stream:
    for number, raw_line in enumerate(stream, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, raw_value = line.partition("=")
        key = key.strip()
        if not separator or key not in allowed:
            raise SystemExit(f"Некорректная строка {number} в файле секретов")
        values = shlex.split(raw_value, comments=True, posix=True)
        if len(values) > 1:
            raise SystemExit(f"Значение в строке {number} нужно заключить в кавычки")
        value = values[0] if values else ""
        sys.stdout.buffer.write(key.encode() + b"\0" + value.encode() + b"\0")
PY
    )
}

load_secret_file

# Логируем весь вывод скрипта запуска
if [[ -d "/workspace" ]]; then
    LOG_FILE="${RUNPOD_LOG_FILE:-/workspace/runpod_startup.log}"
else
    LOG_FILE="${RUNPOD_LOG_FILE:-$SCRIPT_DIR/runpod_startup.log}"
fi
exec > >(tee -i "$LOG_FILE") 2>&1

echo "=== ЗАПУСК КОНТЕЙНЕРА RUNPOD: $(date) ==="

if [[ -z "${PANEL_USER:-}" || -z "${PANEL_PASS:-}" ]]; then
    echo "Ошибка: задайте PANEL_USER и PANEL_PASS через RunPod Secrets или .env.secrets." >&2
    echo "Панель с Terminal не будет запущена без аутентификации." >&2
    exit 2
fi

# Панель запустит ComfyUI как дочерний процесс после установки/обновления.
export AUTO_START_COMFY="${AUTO_START_COMFY:-1}"
export COMFY_ARGS="${COMFY_ARGS:---listen 0.0.0.0 --port 8188 --highvram}"

# Современный многопоточный транспорт Hugging Face. hf_transfer устарел;
# huggingface_hub автоматически использует hf-xet.
export HF_XET_HIGH_PERFORMANCE="${HF_XET_HIGH_PERFORMANCE:-1}"

# Держим тяжелые кэши моделей на persistent storage, а не на container disk.
if [[ -d "/workspace" ]]; then
    export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/workspace/.cache}"
    export PIP_CACHE_DIR="${PIP_CACHE_DIR:-/workspace/.cache/pip}"
    export TORCH_HOME="${TORCH_HOME:-/workspace/.cache/torch}"
    export HF_HOME="${HF_HOME:-/workspace/.cache/huggingface}"
    export HF_HUB_CACHE="${HF_HUB_CACHE:-${HUGGINGFACE_HUB_CACHE:-/workspace/.cache/huggingface/hub}}"
    export HUGGINGFACE_HUB_CACHE="${HUGGINGFACE_HUB_CACHE:-$HF_HUB_CACHE}"
    export DIFFUSERS_CACHE="${DIFFUSERS_CACHE:-/workspace/.cache/huggingface/diffusers}"
    export HF_XET_CACHE="${HF_XET_CACHE:-/workspace/.cache/huggingface/xet}"
    mkdir -p "$PIP_CACHE_DIR" "$TORCH_HOME" \
        "$HF_HOME" "$HF_HUB_CACHE" "$DIFFUSERS_CACHE" \
        "$HF_XET_CACHE"
fi

# Проверяем наличие основного установщика
if [[ -f "$SCRIPT_DIR/comfy_install_runpod.sh" ]]; then
    echo "Обнаружен comfy_install_runpod.sh. Запуск автоматической установки и панели управления..."
    exec bash "$SCRIPT_DIR/comfy_install_runpod.sh"
else
    echo "Ошибка: comfy_install_runpod.sh не найден в директории $SCRIPT_DIR!"
    exit 1
fi
