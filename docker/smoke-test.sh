#!/usr/bin/env bash
set -Eeuo pipefail
image=${1:?Usage: smoke-test.sh IMAGE}
container="comfy-image-check-$$"
volume="comfy-image-check-$$"
cleanup() {
    docker rm -f "$container" >/dev/null 2>&1 || true
    docker volume rm "$volume" >/dev/null 2>&1 || true
}
trap cleanup EXIT
docker volume create "$volume" >/dev/null
# A CPU-only smoke test checks imports, storage, model selection and the API.
# It deliberately selects a template already provisioned with stub files below.
docker run --rm --entrypoint python3 "$image" -c \
    'from comfy_setup_cache import check_imports; check_imports()'
docker run --rm --entrypoint bash -v "$volume:/workspace" "$image" -c '
  mkdir -p /workspace/ComfyUI/output
  printf keep-me > /workspace/ComfyUI/output/preexisting.txt
  export COMFY_DIR=/workspace/ComfyUI
  python3 comfy_template_startup.py prepare --templates 89,93,94
  python3 - <<"PY"
import json, os
from pathlib import Path
base = Path(os.environ["COMFY_DIR"])
for item in json.loads((base / "template_apis/manifest.json").read_text()):
    for model in item["models"]:
        target = base / model
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"smoke-test-placeholder")
PY
'
docker run -d --name "$container" -v "$volume:/workspace" \
    -e PANEL_USER=smoke-test -e PANEL_PASS=smoke-test \
    -e AUTO_START_COMFY=1 -e RUNPOD_BASE_SERVICES=0 \
    -e 'COMFY_ARGS=--cpu --listen 0.0.0.0 --port 8188' \
    -e COMFY_TEMPLATE_IDS=89,93,94 "$image" >/dev/null
for attempt in $(seq 1 60); do
    if docker exec "$container" python3 /opt/runpod-scripts/docker/healthcheck.py 2>/dev/null; then
        break
    fi
    if [[ "$(docker inspect -f '{{.State.Running}}' "$container")" != true ]]; then
        docker logs "$container"
        exit 1
    fi
    sleep 2
done
for attempt in $(seq 1 60); do
    if docker exec "$container" python3 -c \
        'from urllib.request import urlopen; urlopen("http://127.0.0.1:8188/system_stats", timeout=3)' 2>/dev/null; then
        break
    fi
    sleep 2
done
# -i feeds the test script to the container's stdin.
docker exec -i "$container" python3 - <<'PY'
import base64, json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
assert Path('/workspace/ComfyUI/output/preexisting.txt').read_text() == 'keep-me'
assert Path('/opt/ComfyUI/models').resolve() == Path('/workspace/ComfyUI/models')
assert not Path('/opt/runpod-scripts/.env.secrets').exists(), 'Secret file in image'
url = 'http://127.0.0.1:7860/template-apis'
try:
    urlopen(url, timeout=5)
    raise AssertionError('API unexpectedly accessible without authentication')
except HTTPError as exc:
    assert exc.code == 401
auth = 'Basic ' + base64.b64encode(b'smoke-test:smoke-test').decode()
def get(path):
    with urlopen(Request(url + path, headers={'Authorization': auth}), timeout=5) as response:
        return json.load(response)
status = get('')
assert {item['id'] for item in status} == {89, 93, 94}, status
assert all(item['ready'] for item in status), status
assert get('/89/api'), 'API JSON missing'
PY
docker restart "$container" >/dev/null
for attempt in $(seq 1 60); do
    if docker exec "$container" python3 /opt/runpod-scripts/docker/healthcheck.py 2>/dev/null; then
        break
    fi
    sleep 2
done
docker exec "$container" python3 /opt/runpod-scripts/docker/healthcheck.py
docker logs "$container"
docker exec "$container" cat /opt/ComfyUI/template-download.log
echo 'Image smoke test passed; GPU inference is not exercised.'
