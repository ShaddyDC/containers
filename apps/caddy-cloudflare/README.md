# caddy-cloudflare

custom caddy docker image with cloudflare integrations and security extensions.

## modules included

- [caddy-dns/cloudflare](https://github.com/caddy-dns/cloudflare) - cloudflare dns provider for automated certificate issuance
- [WeidiDeng/caddy-cloudflare-ip](https://github.com/WeidiDeng/caddy-cloudflare-ip) - retrieves cloudflare ips from their offical website
- [greenpau/caddy-security](https://github.com/greenpau/caddy-security) - authentication, authorization and access control

## maintenance

image is kept up-to-date via renovate bot, which automatically updates the base image and dependencies.
