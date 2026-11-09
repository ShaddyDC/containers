FROM caddy:builder@sha256:3db11aead97f1fdff9c563d0dd8e7fba2e4c7031bef40f3e44fd1982f3e8366b AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

# Until the base image ships ca-certificates 20261020 (the compromised eMudhra CAs, 2026-10-17)
RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
