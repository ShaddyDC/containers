FROM caddy:builder@sha256:53f91ad7c5f1ab9a607953199b7c1e10920c570ae002aef913d68ed7464fb19f AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
