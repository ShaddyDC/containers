FROM caddy:builder@sha256:e5612b84a4a8c0d452da55d3d7d97985a5039ef3be6e399fd7264bb070f30559 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
