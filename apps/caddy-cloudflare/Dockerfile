FROM caddy:builder@sha256:5b98e8a4c3d077585c5980b205cfcc9602d820675d5e0cfdbf5eeff939dc0b4a AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
