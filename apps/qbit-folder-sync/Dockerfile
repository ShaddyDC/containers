FROM python:3.15-alpine@sha256:0f9552bb28711333da16915ec146f5e6bb44a7fdac9ced15dc17c2e0206346dd AS base

# The base image predates ca-certificates 20261020 (the compromised eMudhra CAs, 2026-10-17)
RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d /uv /bin/uv
# uv must build the venv on the base image's Python: one it downloads itself is not copied to the
# final stage. Keep .python-version in step with the base image tag.
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

FROM base

COPY --from=builder /app /app

# Smoke test in the final stage: the venv's interpreter must exist here (it is a symlink to the
# base image's Python) and the dependencies must import. Fails the build otherwise.
RUN ["/app/.venv/bin/python", "-c", "import qbittorrent"]

# Environment variables
ENV PATH="/app/.venv/bin:$PATH" \
  QBIT_URL="http://localhost:8080" \
  INPUT_DIR="/downloads" \
  OUTPUT_DIR="/output" \
  LOG_LEVEL="INFO" \
  LINK_MODE="hardlink" \
  CONNECTION_RETRIES="3" \
  CONNECTION_RETRY_DELAY="5"

CMD ["/app/.venv/bin/python", "/app/main.py"]

