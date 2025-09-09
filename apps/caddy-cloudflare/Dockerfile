FROM caddy:builder@sha256:5d3e2fc2ba02ecf51ebbfbbea2ce0ab64d3aa80c99722ed929f8bf973be7e831 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
