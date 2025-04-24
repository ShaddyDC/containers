# qbit-folder-sync

lightweight utility that syncs completed torrents from qbittorrent to a target directory, optionally filtering by tracker urls.

## what it does

- finds completed torrents in your qbittorrent instance
- filters by tracker if desired
- creates hardlinks (or copies) to a target directory with clean organization

## usage

### docker

```bash
docker run -e QBIT_URL=http://your-qbit-host:port \
  -e DESIRED_TRACKERS=tracker.site1.org,site2.org \
  -v /path/to/qbit/downloads:/data/downloads:ro \
  -v /path/to/output:/data/output \
  username/qbit-sync
```

### environment variables

| variable | default | description |
|----------|---------|-------------|
| `QBIT_URL` | `http://localhost:8080` | qbittorrent web ui url |
| `QBIT_USER` | (none) | username for qbit webui (optional) |
| `QBIT_PASS` | (none) | password for qbit webui (optional) |
| `INPUT_DIR` | `/data/downloads` | local mount point for qbit files |
| `OUTPUT_DIR` | `/data/output` | output directory |
| `DESIRED_TRACKERS` | (none) | comma-separated tracker urls/fragments to filter by |
| `LINK_MODE` | `hardlink` | `hardlink` or `copy` |
| `LOG_LEVEL` | `INFO` | python logging level |
| `CONNECTION_RETRIES` | `3` | connection retry attempts |
| `CONNECTION_RETRY_DELAY` | `5` | seconds between retries |

## notes

- hardlinks save space but require source/dest on same filesystem
- runs once and exits - use with cron/k8s job/etc for scheduling
- output dir structure: `OUTPUT_DIR/[sanitized_torrent_name]/[file_paths]`
