# containers

containerized applications built for amd64/arm64,
either for utility scripts that do not need their own repository or for providing
simple images for upstream projects that aren't otherwise available.

## about

This repo contains various container images.
They're built using github actions for multi-architecture support, and published to ghcr.io.
The setup is heavily inspired by [home-operations/containers](https://github.com/home-operations/containers).

## usage

The images are hosted on [github container registry](https://github.com/ShaddyDC?tab=packages&repo_name=containers).

```bash
docker pull ghcr.io/shaddydc/qbit-folder-sync:latest
```

## maintenance

Dependency updates are automated via renovate.
Container bases are consistently updated to alpine/python releases.

