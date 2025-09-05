FROM caddy:builder@sha256:3c711fcf9a64d31e8927a2efb538cf99e6f758f737aadcde5fd7dfadc93287a8 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
