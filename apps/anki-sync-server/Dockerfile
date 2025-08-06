FROM rust:1.88.0@sha256:af306cfa71d987911a781c37b59d7d67d934f49684058f96cf72079c3626bfe0 AS builder

# renovate: datasource=github-releases packageName=ankitects/anki versioning=loose
ARG ANKI_VERSION=25.07.5

RUN apt-get update && apt-get install -y build-essential protobuf-compiler && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cargo install --git https://github.com/ankitects/anki.git \
  --tag ${ANKI_VERSION} \
  --root /anki-server  \
  --locked \
  anki-sync-server

FROM gcr.io/distroless/cc-debian12@sha256:bf0494952368db47e9e38eecc325c33f5ee299b1b1ccc5d9e30bdf1e5e4e3a58

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
