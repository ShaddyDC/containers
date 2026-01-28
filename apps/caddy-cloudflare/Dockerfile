FROM caddy:builder@sha256:00dfa5f39333243282c82d73de2acfe0609cb4a7879eb96946dcdfbf3a27ff87 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
