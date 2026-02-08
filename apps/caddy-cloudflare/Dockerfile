FROM caddy:builder@sha256:fbcbf6ec1f6d94bc85be547a4d46ac32d0d8119baeaffc383dee068ba332cb50 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
