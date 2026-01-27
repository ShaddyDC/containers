FROM rust:1.93.0@sha256:4c7eb947d7e078f5c076e086c7b75c36ea0ec7c685f2244b3d79306deb7e44b7 AS builder

# renovate: datasource=github-releases packageName=ankitects/anki versioning=loose
ARG ANKI_VERSION=25.09.2

RUN apt-get update && apt-get install -y build-essential protobuf-compiler && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cargo install --git https://github.com/ankitects/anki.git \
  --tag ${ANKI_VERSION} \
  --root /anki-server  \
  --locked \
  anki-sync-server

FROM gcr.io/distroless/cc-debian12@sha256:0000f9dc0290f8eaf0ecceafbc35e803649087ea7879570fbc78372df7ac649b

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
