FROM python:3.12-alpine@sha256:017a82f185bf6f10e62156f3e89b7e694d56d613b5a3f4dbf1d28f1014a972ed AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:db305ce8edc1c2df4988b9d23471465d90d599cc55571e6501421c173a33bb0b /uv /bin/uv
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
  QBIT_SAVE_PATH_PREFIX="/downloads" \
  LOCAL_INPUT_DIR="/downloads" \
  OUTPUT_DIR="/output" \
  LOG_LEVEL="INFO" \
  LINK_MODE="hardlink" \
  CONNECTION_RETRIES="3" \
  CONNECTION_RETRY_DELAY="5"

CMD ["/app/.venv/bin/python", "/app/main.py"]

