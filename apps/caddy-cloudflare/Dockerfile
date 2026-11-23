FROM caddy:builder@sha256:aef223d1f943bc12a29a9e0a0a73983aa19a36672daede7507da4201a6b1016a AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

# Until the base image ships ca-certificates 20261020 (the compromised eMudhra CAs, 2026-10-17)
RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
