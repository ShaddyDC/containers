FROM caddy:builder@sha256:7838e973e96b0e5f74213bf9f3c0f35089dc2e812e4c0b20790e45c6512423fb AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
