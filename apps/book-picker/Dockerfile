FROM python:3.14-alpine@sha256:7af51ebeb83610fb69d633d5c61a2efb87efa4caf66b59862d624bb6ef788345 AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:798712e57f879c5393777cbda2bb309b29fcdeb0532129d4b1c3125c5385975a /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

RUN echo "Running tests..." && \
    .venv/bin/python -m unittest /app/test_selector.py && \
    echo "Tests passed."

FROM base

COPY --from=builder /app /app

# Environment variables
ENV PATH="/app/.venv/bin:$PATH" \
  ROOT_DIR="/data/books" \
  BASE_URL="https://example.com" \
  DISCORD_WEBHOOK="" \
  N_FILES=5

CMD ["/app/.venv/bin/python", "/app/main.py"]

