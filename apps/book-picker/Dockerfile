FROM python:3.13-alpine@sha256:452682e4648deafe431ad2f2391d726d7c52f0ff291be8bd4074b10379bb89ff AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:0178a92d156b6f6dbe60e3b52b33b421021f46d634aa9f81f42b91445bb81cdf /uv /bin/uv
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

