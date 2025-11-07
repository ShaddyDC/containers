FROM caddy:builder@sha256:4535684b970f048a772efec86ce46148a0e916a653e73d9b223cb2ad07f5dfe6 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
