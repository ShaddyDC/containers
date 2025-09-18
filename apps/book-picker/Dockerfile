FROM python:3.13-alpine@sha256:9ba6d8cbebf0fb6546ae71f2a1c14f6ffd2fdab83af7fa5669734ef30ad48844 AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:62022a082ce1358336b920e9b7746ac7c95b1b11473aa93ab5e4f01232d6712d /uv /bin/uv
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

