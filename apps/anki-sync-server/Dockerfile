FROM rust:1.88.0@sha256:5771a3cc2081935c59ac52b92d49c9e164d4fed92c9f6420aa8cc50364aead6e AS builder

# renovate: datasource=github-releases packageName=ankitects/anki versioning=loose
ARG ANKI_VERSION=25.07.3

RUN apt-get update && apt-get install -y build-essential protobuf-compiler && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN cargo install --git https://github.com/ankitects/anki.git \
  --tag ${ANKI_VERSION} \
  --root /anki-server  \
  --locked \
  anki-sync-server

FROM gcr.io/distroless/cc-debian12@sha256:eccec5274132c1be0ce5d2c8e6fe41033e64af5e987ccee9007826e4c012069d

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
