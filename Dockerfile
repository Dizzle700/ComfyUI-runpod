# syntax=docker/dockerfile:1
ARG BASE_IMAGE=runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404@sha256:0a360022e8de4375af99430f84e8b38951acc397252163a37ceac7204d01be35
FROM ${BASE_IMAGE}

ARG COMFY_COMMIT=651ca296a73cd21c12a57eb8741d52e40dc6528f
ARG MANAGER_COMMIT=6db282e2488cfb0833fbf38d74baffcd716ce8f6
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    COMFY_DIR=/opt/ComfyUI \
    COMFY_DATA_DIR=/workspace/ComfyUI
WORKDIR /opt/runpod-scripts

RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl aria2 ca-certificates util-linux tini libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Keep this expensive layer cached when panel/downloader code changes.
COPY requirements.txt comfy_install_runpod.sh comfy_setup_cache.py ./
COPY docker/build.sh /opt/image-build.sh
RUN bash /opt/image-build.sh "$COMFY_COMMIT" "$MANAGER_COMMIT"

ARG SOURCE_REVISION=local
LABEL org.opencontainers.image.source="https://github.com/Dizzle700/ComfyUI-runpod" \
      org.opencontainers.image.revision="${SOURCE_REVISION}"
COPY runpod_startup.sh comfy_control_panel.py comfy_model_downloader.sh \
     comfy_template_startup.py KRea.txt ./
COPY templates_models.db* faq/templates_models.db* ./
COPY docker/ /opt/runpod-scripts/docker/
RUN python3 -m compileall -q /opt/runpod-scripts || true
ENV COMFY_PREBUILT=1
EXPOSE 7860 8188 22
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD ["python3", "/opt/runpod-scripts/docker/healthcheck.py"]
ENTRYPOINT ["/usr/bin/tini", "-g", "--", "bash", "/opt/runpod-scripts/docker/entrypoint.sh"]
CMD []
