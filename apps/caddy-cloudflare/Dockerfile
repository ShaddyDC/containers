FROM caddy:builder@sha256:c7237a4e4b7d31b697a8672c7418be98471a3f30f44477e3fa36b9d16df35797 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
