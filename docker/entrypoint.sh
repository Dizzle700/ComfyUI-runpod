#!/usr/bin/env bash
set -Eeuo pipefail
export COMFY_DIR=/opt/ComfyUI COMFY_PREBUILT=1
python3 /opt/runpod-scripts/docker/prepare_storage.py \
    --comfy-dir "$COMFY_DIR" --data-dir "${COMFY_DATA_DIR:-/workspace/ComfyUI}"

# Preserve RunPod's SSH/Jupyter startup contract. The panel is the main service.
if [[ "${RUNPOD_BASE_SERVICES:-1}" == 1 && -f /start.sh ]]; then
    /start.sh &
fi
exec bash /opt/runpod-scripts/runpod_startup.sh "$@"
