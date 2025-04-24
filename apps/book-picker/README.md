# book-picker

selects random files from a directory structure and posts them to a discord webhook with search links.

## what it does

- scans for files in configured directory
- randomly selects n files
- generates direct access urls and search links
- posts formatted message to discord webhook

## config

environment variables:
- `ROOT_DIR`: base directory to scan (default: `/data/books`)
- `BASE_URL`: base url for file access links (default: `https://example.com`)
- `DISCORD_WEBHOOK`: required webhook url for posting
- `N_FILES`: number of files to select (default: `5`)
- `SEARCH_ENGINE`: search provider to use - "kagi" or "google" (default: `kagi`)

## usage

run in container or locally with proper environment variables set.

```
docker run -e DISCORD_WEBHOOK=https://... -v /your/files:/data/books book-picker
```

outputs formatted discord message with random file selections and search links.
