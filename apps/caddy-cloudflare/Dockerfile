FROM caddy:builder@sha256:c9fd63066cb907c05488886402ed9869ba8b90741a6af2d85b33ab43ba94f342 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
