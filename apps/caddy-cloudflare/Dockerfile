FROM caddy:builder@sha256:c1e0d8e7fe650596356c46319c8c47890045bf3cd4c3d2fc6463a7ff541a99c8 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
