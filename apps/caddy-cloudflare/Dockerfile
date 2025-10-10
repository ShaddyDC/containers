FROM caddy:builder@sha256:5ffdd1eb7c262d118977dfd8c4a0c34c7781366fbadef3b4daeac459cb30e99e AS builder

RUN xcaddy build \
  --with github.com/caddy-dns/cloudflare \
  --with github.com/WeidiDeng/caddy-cloudflare-ip \
  --with github.com/greenpau/caddy-security

FROM caddy:latest

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
