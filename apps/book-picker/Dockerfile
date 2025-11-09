FROM python:3.13-alpine@sha256:e5fa639e49b85986c4481e28faa2564b45aa8021413f31026c3856e5911618b1 AS base

FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:latest@sha256:08f409e1d53e77dfb5b65c788491f8ca70fe1d2d459f41c89afa2fcbef998abe /uv /bin/uv
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

