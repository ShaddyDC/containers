FROM caddy:builder@sha256:c2fc374fd352439d76e1777b28d97d9f6d9c1dd86116db9227460374d46097d5 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

# Until the base image ships ca-certificates 20261020 (the compromised eMudhra CAs, 2026-10-17)
RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
