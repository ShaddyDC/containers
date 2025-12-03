FROM caddy:builder@sha256:fe404674d209455fdef351db5437758ee0e70a6b59abe770663c09cfa05dbddf AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
