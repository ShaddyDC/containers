FROM caddy:builder@sha256:d300ab11c67d279f272a6b8420bc381a66ac696a16c2a7aa55ea0262e705d78e AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
