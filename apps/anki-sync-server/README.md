# anki-sync-server

containerized [anki sync server](https://docs.ankiweb.net/sync-server.html) with automated dependency updates.

this provides a minimal, always-updated docker image for self-hosting anki sync instead of relying on ankiweb.
built from the official anki rust implementation using distroless base for smaller attack surface.

## usage

```bash
# basic single user setup
docker run -d \
  -e "SYNC_USER1=user:password" \
  -p 8080:8080 \
  -v anki-data:/anki_data \
  --name anki-sync \
  ghcr.io/shaddydc/anki-sync-server:latest
```

```bash
# multiple users
docker run -d \
  -e "SYNC_USER1=alice:secret123" \
  -e "SYNC_USER2=bob:different456" \
  -p 8080:8080 \
  -v anki-data:/anki_data \
  --name anki-sync \
  ghcr.io/shaddydc/anki-sync-server:latest
```

then configure your anki clients to sync to `http://your-server:8080/`

## configuration

| env var | description | default |
|---------|-------------|---------|
| `SYNC_USER1` | first user (required) `username:password` | - |
| `SYNC_USER2-N` | additional users | - |
| `SYNC_HOST` | bind address | `0.0.0.0` |
| `MAX_SYNC_PAYLOAD_MEGS` | upload limit | `100` |
| `PASSWORDS_HASHED` | use hashed passwords | `0` |

`SYNC_PORT` and `SYNC_BASE` are fixed at `8080` and `/anki_data` for container consistency.

## vs upstream

- **automated updates**: renovate keeps anki version current
- **distroless base**: smaller image, reduced attack surface  
- **volume persistence**: data survives container recreation
- **multi-arch**: amd64/arm64 support
- **healthcheck**: built-in container health monitoring

the [upstream dockerfile](https://github.com/ankitects/anki/tree/main/docs/syncserver) offers more customization but requires manual maintenance.

## security notes

- runs over http - use behind reverse proxy with tls for internet exposure
- consider using hashed passwords for production
- restrict network access if possible (vpn, local network only)

## client setup

each device needs the sync server url configured:
- desktop: preferences → network → sync server  
- ankidroid: settings → advanced → custom sync server
- ankimobile: ios settings → anki → toggle "allow local network" if connecting locally

older clients may need separate endpoints:
- sync: `http://server:8080/sync/`  
- media: `http://server:8080/msync/`
