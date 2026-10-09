"""Panel readiness; model downloads and manual ComfyUI stops do not fail health."""
from urllib.request import urlopen
with urlopen('http://127.0.0.1:7860/openapi.json', timeout=3) as response:
    if response.status != 200:
        raise SystemExit(1)
