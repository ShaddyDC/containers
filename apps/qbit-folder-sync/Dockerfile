FROM python:3.13-alpine@sha256:18159b2be11db91f84b8f8f655cd860f805dbd9e49a583ddaac8ab39bf4fe1a7 AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:87a04222b228501907f487b338ca6fc1514a93369bfce6930eb06c8d576e58a4 /uv /bin/uv
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

