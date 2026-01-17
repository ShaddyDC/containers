FROM caddy:builder@sha256:b6424b4a90e25fde5cb9fd8e1da716159a313869ac3ba1c34b11c50781acab81 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
