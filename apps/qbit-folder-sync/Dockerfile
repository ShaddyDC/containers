FROM python:3.13-alpine@sha256:37b14db89f587f9eaa890e4a442a3fe55db452b69cca1403cc730bd0fbdc8aaf AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:a7999d42cba0e5af47ef3c06ac310229c7f29c5314e35902f8353e8e170eeed1 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

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

