FROM python:3.14-alpine@sha256:8373231e1e906ddfb457748bfc032c4c06ada8c759b7b62d9c73ec2a3c56e710 AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:f6e3549ed287fee0ddde2460a2a74a2d74366f84b04aaa34c1f19fec40da8652 /uv /bin/uv
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

