FROM caddy:builder@sha256:10ed0251c5cd1dbb4db0b71ad43121147961a51adfec35febce2c93ea25c24f4 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
