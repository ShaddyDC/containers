FROM caddy:builder@sha256:d842facfd63b960922e57444ff76fd8f0793a66dfdcf481af8026e1f4e6a39b4 AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

# Until the base image ships ca-certificates 20261020 (the compromised eMudhra CAs, 2026-10-17)
RUN apk upgrade --no-cache ca-certificates ca-certificates-bundle

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
