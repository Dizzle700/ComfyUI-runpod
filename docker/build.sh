#!/usr/bin/env bash
set -Eeuo pipefail
comfy_commit=${1:?ComfyUI SHA is required}
manager_commit=${2:?Manager SHA is required}
[[ "$comfy_commit" =~ ^[0-9a-f]{40}$ && "$manager_commit" =~ ^[0-9a-f]{40}$ ]]

checkout() {
    local repo=$1 destination=$2 commit=$3
    mkdir -p "$destination"
    git -C "$destination" init
    git -C "$destination" remote add origin "$repo"
    git -C "$destination" fetch --depth 1 origin "$commit"
    git -C "$destination" checkout --detach FETCH_HEAD
    [[ "$(git -C "$destination" rev-parse HEAD)" == "$commit" ]]
}
checkout https://github.com/Comfy-Org/ComfyUI.git "$COMFY_DIR" "$comfy_commit"
checkout https://github.com/Comfy-Org/ComfyUI-Manager.git \
    "$COMFY_DIR/custom_nodes/comfyui-manager" "$manager_commit"
bash /opt/runpod-scripts/comfy_install_runpod.sh --no-start
python3 -m pip freeze --all > /opt/python-packages.txt
python3 - "$comfy_commit" "$manager_commit" <<'PY'
import json, sys
from pathlib import Path
Path('/opt/image-versions.json').write_text(json.dumps({
    'comfy_commit': sys.argv[1], 'manager_commit': sys.argv[2],
    'python_packages': '/opt/python-packages.txt',
}, indent=2) + '\n')
PY
