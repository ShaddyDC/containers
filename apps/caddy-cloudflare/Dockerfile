FROM caddy:builder@sha256:acf9b51367f2cdd94a5621b1d5f37a3d095b5f6e2157c83b48d2b1f127576366 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
