FROM python:3.13-alpine@sha256:a94caf6aab428e086bc398beaf64a6b7a0fad4589573462f52362fd760e64cc9 AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:563b73ab264117698521303e361fb781a0b421058661b4055750b6c822262d1e /uv /bin/uv
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

