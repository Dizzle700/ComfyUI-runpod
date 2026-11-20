#!/usr/bin/env bash

set -Eeuo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# На RunPod используем /workspace/ComfyUI для сохранения данных после перезапуска пода
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "/workspace" ]]; then
    COMFY_DIR="${COMFY_DIR:-/workspace/ComfyUI}"
else
    COMFY_DIR="${COMFY_DIR:-$SCRIPT_DIR/ComfyUI}"
fi
export COMFY_DIR

if [[ -d "/workspace" ]]; then
    export HF_XET_HIGH_PERFORMANCE="${HF_XET_HIGH_PERFORMANCE:-1}"
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

START_PANEL=true
UPDATE_ON_START="${COMFY_UPDATE_ON_START:-0}"
FORCE_INSTALL="${COMFY_FORCE_INSTALL:-0}"
for arg in "$@"; do
    case "$arg" in
        --no-start) START_PANEL=false ;;
        --update) UPDATE_ON_START=1 ;;
        --reinstall) FORCE_INSTALL=1 ;;
        --help|-h)
            cat <<'EOF'
Использование:
  comfy_install_runpod.sh [--no-start] [--update] [--reinstall]

Опции:
  --no-start    Установить/обновить ComfyUI без запуска панели управления.
  --update      Обновить ComfyUI и Manager и выполнить pip install.
  --reinstall   Выполнить pip install даже при действующей отметке установки.
EOF
            exit 0
            ;;
        *) echo "Неизвестная опция: $arg" >&2; exit 2 ;;
    esac
done
if [[ ! "$UPDATE_ON_START" =~ ^[01]$ || ! "$FORCE_INSTALL" =~ ^[01]$ ]]; then
    echo "COMFY_UPDATE_ON_START и COMFY_FORCE_INSTALL должны быть 0 или 1." >&2
    exit 2
fi

COMFY_REPO="https://github.com/Comfy-Org/ComfyUI.git"
MANAGER_DIR="$COMFY_DIR/custom_nodes/comfyui-manager"
MANAGER_REPO="https://github.com/Comfy-Org/ComfyUI-Manager.git"

info() { printf '%b\n' "${BLUE}$*${NC}"; }
success() { printf '%b\n' "${GREEN}$*${NC}"; }
warn() { printf '%b\n' "${YELLOW}$*${NC}"; }
error() { printf '%b\n' "${RED}$*${NC}" >&2; }

on_error() {
    local exit_code=$?
    error "Ошибка на строке $1 (код: $exit_code). Установка остановлена."
    exit "$exit_code"
}
trap 'on_error "$LINENO"' ERR

# Проверка окружения RunPod
if [[ -d "/workspace" ]]; then
    info "Каталог /workspace доступен. ComfyUI: $COMFY_DIR."
else
    warn "Каталог /workspace не найден. Данные могут быть потеряны при остановке пода."
fi

ensure_python_pip() {
    if "$PYTHON_EXE" -m pip --version >/dev/null 2>&1; then
        success "pip готов к работе: $("$PYTHON_EXE" -m pip --version)"
        return
    fi

    info "pip не найден в Python-окружении RunPod. Устанавливаем через ensurepip..."
    "$PYTHON_EXE" -m ensurepip --upgrade
}

write_preinstalled_torch_constraints() {
    TORCH_CONSTRAINTS="$COMFY_DIR/.runpod-torch-constraints.txt"
    "$PYTHON_EXE" - <<'PY' > "$TORCH_CONSTRAINTS"
from importlib.metadata import PackageNotFoundError, version

for package in ("torch", "torchvision", "torchaudio"):
    try:
        print(f"{package}=={version(package)}")
    except PackageNotFoundError:
        pass
print("transformers>=4.46.2,<5.0.0")
print("gradio>=5.5.0,<6.0.0")
print("huggingface-hub>=0.34.0,<1.0.0")
PY
}

has_cuda_torch() {
    local python_exe=$1
    "$python_exe" - <<'PY' >/dev/null 2>&1
import torch

raise SystemExit(0 if torch.version.cuda else 1)
PY
}

download_startup_model_packages() {
    local packages=${COMFY_MODEL_PACKAGES:-}
    local package_file="$SCRIPT_DIR/KRea.txt"

    [[ -n "$packages" ]] || return 0
    if [[ ! -r "$package_file" ]]; then
        error "Файл пакетов моделей не найден: $package_file"
        return 0
    fi

    info "Загружаем пакеты моделей из KRea.txt: $packages"
    if ! COMFY_DIR="$COMFY_DIR" bash "$SCRIPT_DIR/comfy_model_downloader.sh" \
        --batch "$package_file" --packages "$packages"; then
        warn "Не все пакеты моделей скачались успешно. Панель будет запущена; проверьте лог выше."
    else
        success "Все запрошенные пакеты моделей подготовлены."
    fi
}

start_template_downloads() {
    local ids=${COMFY_TEMPLATE_IDS:-}
    local helper="$SCRIPT_DIR/comfy_template_startup.py"
    local log_file="$COMFY_DIR/template-download.log"
    [[ -n "$ids" ]] || return 0
    [[ -f "$helper" ]] || { error "Не найден $helper"; return 1; }
    "$PYTHON_EXE" "$helper" prepare --templates "$ids" \
        --workers "${COMFY_TEMPLATE_DOWNLOAD_WORKERS:-2}"
    info "API JSON готовы в $COMFY_DIR/template_apis; загрузка моделей пойдет в фоне."
    PYTHONUNBUFFERED=1 nohup flock -n "$COMFY_DIR/.template-download.lock" \
        "$PYTHON_EXE" "$helper" download --skip-prepare --templates "$ids" \
        --workers "${COMFY_TEMPLATE_DOWNLOAD_WORKERS:-2}" \
        >> "$log_file" 2>&1 < /dev/null &
    info "Лог фоновой загрузки: $log_file (PID $!)"
}

PYTHON_EXE="${PYTHON_EXE:-python3}"
SETUP_CACHE_HELPER="$SCRIPT_DIR/comfy_setup_cache.py"
SETUP_STAMP="$COMFY_DIR/.runpod-setup.json"

if [[ "${COMFY_PREBUILT:-0}" == 1 ]]; then
    if [[ "$UPDATE_ON_START" == 1 || "$FORCE_INSTALL" == 1 ]]; then
        error "В готовом образе версии закреплены. Для обновления соберите новый image."
        exit 2
    fi
    if [[ ! -f "$SETUP_STAMP" ]]; then
        error "Отметка готового образа не найдена ($SETUP_STAMP). Пересоздайте контейнер из image."
        exit 1
    fi
    if [[ "${COMFY_VERIFY_ON_START:-0}" == 1 ]]; then
        if ! "$PYTHON_EXE" "$SETUP_CACHE_HELPER" check \
            --comfy-dir "$COMFY_DIR" --script-dir "$SCRIPT_DIR"; then
            error "Окружение готового образа изменено или повреждено. Пересоздайте контейнер из image."
            exit 1
        fi
    fi
    info "Готовый Docker image: git pull и pip install при запуске не выполняются."
else
# Клонируем или обновляем ComfyUI
if [[ ! -d "$COMFY_DIR/.git" ]]; then
    info "Клонируем репозиторий ComfyUI..."
    git clone --depth 1 "$COMFY_REPO" "$COMFY_DIR"
elif [[ "$UPDATE_ON_START" == 1 ]]; then
    info "Репозиторий ComfyUI уже существует. Обновляем..."
    git -C "$COMFY_DIR" pull --ff-only
else
    info "Используем сохранённую версию ComfyUI (для обновления: --update)."
fi

cd "$COMFY_DIR"
PYTHON_EXE="${PYTHON_EXE:-python3}"
export PIP_BREAK_SYSTEM_PACKAGES="${PIP_BREAK_SYSTEM_PACKAGES:-1}"
ensure_python_pip

# Используем готовое Python-окружение RunPod напрямую. Constraints запрещают pip
# подменять предустановленный Torch другой сборкой.
if has_cuda_torch "$PYTHON_EXE"; then
    success "Используем предустановленный PyTorch: $("$PYTHON_EXE" -c 'import torch; print(torch.__version__, "(CUDA", torch.version.cuda, ")")')"
    if ! "$PYTHON_EXE" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)" >/dev/null 2>&1; then
        warn "PyTorch собран с CUDA, но GPU сейчас недоступен. Проверьте драйвер и настройки RunPod."
    fi
else
    error "CUDA-enabled PyTorch в RunPod-образе не найден."
    error "Выберите PyTorch template; автоматическая загрузка другой сборки отключена."
    exit 1
fi

write_preinstalled_torch_constraints
PIP_TORCH_ARGS=(--constraint "$TORCH_CONSTRAINTS")
export PIP_CONSTRAINT="$TORCH_CONSTRAINTS"

info "Подготавливаем ComfyUI-Manager..."
mkdir -p "$COMFY_DIR/custom_nodes"
if [[ ! -d "$MANAGER_DIR" ]]; then
    git clone --depth 1 "$MANAGER_REPO" "$MANAGER_DIR"
elif [[ "$UPDATE_ON_START" == 1 ]]; then
    git -C "$MANAGER_DIR" pull --ff-only
else
    info "Используем сохранённую версию ComfyUI-Manager."
fi

SETUP_CACHE_HELPER="$SCRIPT_DIR/comfy_setup_cache.py"
SETUP_STAMP="$COMFY_DIR/.runpod-setup.json"
INSTALL_DEPENDENCIES=true
if [[ "$UPDATE_ON_START" == 0 && "$FORCE_INSTALL" == 0 ]]; then
    if "$PYTHON_EXE" "$SETUP_CACHE_HELPER" check \
        --comfy-dir "$COMFY_DIR" --script-dir "$SCRIPT_DIR"; then
        INSTALL_DEPENDENCIES=false
    fi
else
    info "Запрошена принудительная проверка зависимостей через pip."
fi

if [[ "$INSTALL_DEPENDENCIES" == true ]]; then
    # Прерванная установка не должна оставлять старую отметку готовности.
    rm -f -- "$SETUP_STAMP"
    info "Устанавливаем зависимости ComfyUI..."
    "$PYTHON_EXE" -m pip install \
        -r "$COMFY_DIR/requirements.txt" \
        "${PIP_TORCH_ARGS[@]}"

    if [[ -f "$MANAGER_DIR/requirements.txt" ]]; then
        "$PYTHON_EXE" -m pip install \
            -r "$MANAGER_DIR/requirements.txt" \
            "${PIP_TORCH_ARGS[@]}"
    fi

    info "Устанавливаем зависимости панели и совместимый T5/SentencePiece tokenizer..."
    if "$PYTHON_EXE" -m pip show hf-gradio >/dev/null 2>&1; then
        warn "Удаляем несовместимый пакет hf-gradio из RunPod image..."
        "$PYTHON_EXE" -m pip uninstall -y hf-gradio
    fi
    "$PYTHON_EXE" -m pip install \
        -r "$SCRIPT_DIR/requirements.txt" \
        "${PIP_TORCH_ARGS[@]}"
    "$PYTHON_EXE" "$SETUP_CACHE_HELPER" save \
        --comfy-dir "$COMFY_DIR" --script-dir "$SCRIPT_DIR"
fi

fi # COMFY_PREBUILT

# Копирование pisa_sr.pkl, если он лежит в папке со скриптом
if [[ -f "$SCRIPT_DIR/pisa_sr.pkl" ]]; then
    info "Обнаружен локальный файл pisa_sr.pkl. Копируем в ComfyUI..."
    mkdir -p "$COMFY_DIR/models/loras"
    cp "$SCRIPT_DIR/pisa_sr.pkl" "$COMFY_DIR/models/loras/pisa_sr.pkl"
fi

# Пакеты передаются из runpod_startup.sh через --models ИМЯ. Они выбираются
# по заголовкам #ИМЯ внутри KRea.txt.
# Здесь каталог ComfyUI и его models/ уже существуют, поэтому загрузчик может
# корректно определить назначение каждой модели.
download_startup_model_packages
start_template_downloads

success "Автоматическая установка ComfyUI в Python-окружение RunPod завершена!"
if [[ "$START_PANEL" == true ]]; then
    info "Запускаем Графическую Панель Управления..."
    exec "$PYTHON_EXE" "$SCRIPT_DIR/comfy_control_panel.py"
fi
info "Флаг --no-start указан: панель управления не запускаем."
