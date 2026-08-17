FROM rust:1.97.1@sha256:b1b3c9c0d921d7fa0a6d1f9ec7e4eab87f8c8ec97644c3d791450f131dec813f AS builder

# renovate: datasource=github-releases packageName=ankitects/anki versioning=loose
ARG ANKI_VERSION=26.05

RUN apt-get update && apt-get install -y build-essential protobuf-compiler && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cargo install --git https://github.com/ankitects/anki.git \
  --tag ${ANKI_VERSION} \
  --root /anki-server  \
  --locked \
  anki-sync-server

FROM gcr.io/distroless/cc-debian12@sha256:e8e7ee4b8b106d4c5fde9e422a321b2b8a2d5cca546c97adcce927f3e1d36e36

COPY --from=builder /anki-server/bin/anki-sync-server /usr/bin/anki-sync-server

# Note that as a user of the container you should NOT overwrite these values
# for safety and simplicity reasons
ENV SYNC_PORT=8080
ENV SYNC_BASE=/anki_data

EXPOSE ${SYNC_PORT}

CMD ["anki-sync-server"]

# This health check will work for Anki versions 24.08.x and newer.
# For older versions, it may incorrectly report an unhealthy status, which should not be the case.
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ["anki-sync-server", "--healthcheck"]

VOLUME /anki_data

# Image is taken with slight adjustment from
# https://github.com/ankitects/anki/tree/main/docs/syncserver
LABEL maintainer="Jean Khawand <jk@jeankhawand.com>"
