FROM caddy:builder@sha256:369218c81ca6d6af249981221b3a5c764d886dd5b058f51d144066de13f2418d AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
