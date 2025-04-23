#!/usr/bin/env python

import os
import sys
import logging
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

# using python-qbittorrent library (make sure it's installed)
try:
    from qbittorrent import Client
except ImportError:
    print(
        "error: 'python-qbittorrent' library not found. pip install python-qbittorrent",
        file=sys.stderr,
    )
    sys.exit(1)

# --- configuration ---
# load config from environment variables w/ defaults
config = {
    "qbit_url": os.getenv("QBIT_URL", "http://localhost:8080"),
    "qbit_user": os.getenv("QBIT_USER"),
    "qbit_pass": os.getenv("QBIT_PASS"),
    "qbit_save_path_prefix": Path(
        os.getenv("QBIT_SAVE_PATH_PREFIX", "/downloads")
    ),  # path prefix *on the qbittorrent server's filesystem*
    "local_input_dir": Path(
        os.getenv("LOCAL_INPUT_DIR", "/data/downloads")
    ),  # where qbit_save_path_prefix is mounted *locally*
    "output_dir": Path(os.getenv("OUTPUT_DIR", "/data/output")),
    "desired_trackers": set(
        filter(None, os.getenv("DESIRED_TRACKERS", "").split(","))
    ),  # comma-separated tracker urls (or parts)
    "link_mode": os.getenv("LINK_MODE", "hardlink").lower(),  # 'hardlink' or 'copy'
    "log_level": os.getenv("LOG_LEVEL", "INFO").upper(),
    "connection_retries": int(os.getenv("CONNECTION_RETRIES", "3")),
    "connection_retry_delay": int(os.getenv("CONNECTION_RETRY_DELAY", "5")),
}

# --- logging setup ---
logging.basicConfig(
    level=config["log_level"],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%y-%m-%d %h:%m:%s",
)
logger = logging.getLogger("qbit-sync")
# tone down noisy libraries
logging.getLogger("requests").setLevel(logging.WARN)
logging.getLogger("urllib3").setLevel(logging.WARN)


# --- helper functions ---
def sanitize_filename(name: str) -> str:
    """basic sanitization for creating directory names."""
    name = name.replace(" ", ".")
    return "".join(c for c in name if c.isalnum() or c in (".", "-", "_"))


def connect_client(
    retries: int = config["connection_retries"],
    delay: int = config["connection_retry_delay"],
) -> Optional[Client]:
    """establish connection to qbittorrent with retries."""
    for attempt in range(retries + 1):
        try:
            logger.info(f"connecting to qbittorrent at {config['qbit_url']}...")
            client = Client(config["qbit_url"])

            # only try to login if credentials are provided
            if config["qbit_user"] and config["qbit_pass"]:
                client.login(username=config["qbit_user"], password=config["qbit_pass"])
                logger.info("authenticated successfully")
            else:
                logger.info("no credentials provided, skipping authentication")

            logger.info(
                "connection successful. client version: %s, api version: %s",
                client.qbittorrent_version,
                client.api_version,
            )
            return client
        except Exception as e:
            logger.warning(
                f"connection attempt {attempt + 1}/{retries + 1} failed: {e}"
            )
            if attempt < retries:
                logger.info(f"retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error("failed to connect to qbittorrent after multiple retries.")
                return None
    return None


class QbitSync:
    """handles the torrent syncing logic."""

    def __init__(self, client: Client, cfg: Dict[str, Any]):
        self.client = client
        self.cfg = cfg
        self.qbit_save_path_prefix = cfg["qbit_save_path_prefix"]
        self.local_input_dir = cfg["local_input_dir"]
        self.output_dir = cfg["output_dir"]
        self.desired_trackers = cfg["desired_trackers"]
        self.link_mode = cfg["link_mode"]

        if not self.desired_trackers:
            logger.warning(
                "no desired_trackers specified. script will try to sync *all* completed torrents."
            )
        if self.link_mode not in ["hardlink", "copy"]:
            logger.error(
                f"invalid link_mode '{self.link_mode}'. must be 'hardlink' or 'copy'. exiting."
            )
            sys.exit(1)
        logger.info("sync configuration:")
        logger.info(f"  - qbit url: {self.cfg['qbit_url']}")
        logger.info(f"  - qbit save path prefix (server): {self.qbit_save_path_prefix}")
        logger.info(f"  - local input dir (mount): {self.local_input_dir}")
        logger.info(f"  - output dir: {self.output_dir}")
        logger.info(f"  - desired trackers: {self.desired_trackers or 'any'}")
        logger.info(f"  - link mode: {self.link_mode}")

    def _is_desired_torrent(self, torrent_info: Dict[str, Any]) -> bool:
        """check if the torrent matches the desired trackers."""
        if not self.desired_trackers:
            return True  # sync all if no specific trackers are desired

        try:
            trackers = self.client.get_torrent_trackers(
                torrent_hash=torrent_info["hash"]
            )
            for tracker in trackers:
                if any(dt in tracker["url"] for dt in self.desired_trackers):
                    logger.debug(
                        f"torrent '{torrent_info['name']}' matched desired tracker via url '{tracker['url']}'"
                    )
                    return True
            logger.debug(
                f"torrent '{torrent_info['name']}' did not match any desired trackers."
            )
            return False
        except Exception as e:
            logger.exception(
                f"unexpected error getting trackers for '{torrent_info['name']}': {e}"
            )
            return False

    def _get_torrent_properties(self, torrent_hash: str) -> Optional[Dict[str, Any]]:
        """fetch torrent properties."""
        try:
            return self.client.get_torrent(torrent_hash=torrent_hash)
        except Exception as e:
            logger.exception(
                f"unexpected error getting properties for hash {torrent_hash}: {e}"
            )
            return None

    def _get_torrent_files(self, torrent_hash: str) -> Optional[List[Dict[str, Any]]]:
        """fetch list of files for a torrent."""
        try:
            return self.client.get_torrent_files(torrent_hash=torrent_hash)
        except Exception as e:
            logger.exception(
                f"unexpected error getting files for hash {torrent_hash}: {e}"
            )
            return None

    def _calculate_local_src_path(
        self, properties: Dict[str, Any], file_info: Dict[str, Any]
    ) -> Optional[Path]:
        """calculate the local source path using configured path mapping."""
        try:
            server_file_path = Path(properties["save_path"]) / file_info["name"]
            relative_path = server_file_path.relative_to(self.qbit_save_path_prefix)
            local_src = self.local_input_dir / relative_path
            return local_src
        except ValueError as e:
            logger.error(
                f"path mapping error for file '{file_info['name']}' in torrent '{properties['name']}'. "
                f"server path '{server_file_path}' may not be relative to prefix '{self.qbit_save_path_prefix}'. error: {e}"
            )
            return None
        except KeyError as e:
            logger.error(
                f"missing expected key ('save_path' or 'name') for torrent/file. data: {properties}, {file_info}. error: {e}"
            )
            return None
        except Exception as e:
            logger.exception(
                f"unexpected error calculating local source path for '{file_info.get('name', 'unknown file')}': {e}"
            )
            return None

    def _link_or_copy_file(self, src: Path, dst: Path) -> bool:
        """create link or copy file based on configuration."""
        if dst.exists():
            logger.debug(f"destination exists, skipping: {dst}")
            return True

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if self.link_mode == "hardlink":
                logger.debug(f"hardlinking: {src} -> {dst}")
                os.link(src, dst)
            elif self.link_mode == "copy":
                logger.debug(f"copying: {src} -> {dst}")
                shutil.copy2(src, dst)
            else:
                logger.error(f"internal error: invalid link_mode '{self.link_mode}'")
                return False
            return True
        except FileNotFoundError:
            logger.error(f"source file not found: {src}")
            return False
        except OSError as e:
            logger.error(f"os error linking/copying {src} to {dst}: {e}")
            if (
                self.link_mode == "hardlink"
                and "invalid cross-device link" in str(e).lower()
            ):
                logger.warning(
                    "hardlink failed (likely cross-device). consider setting link_mode=copy if source/dest are on different filesystems."
                )
            return False
        except Exception as e:
            logger.exception(f"unexpected error linking/copying {src} to {dst}: {e}")
            return False

    def process_torrent(self, torrent_info: Dict[str, Any]) -> None:
        """process a single torrent: get files, calculate paths, link/copy."""
        torrent_hash = torrent_info.get("hash")
        torrent_name = torrent_info.get("name", f"unknown_hash_{torrent_hash}")
        if not torrent_hash:
            logger.error(f"torrent info missing 'hash': {torrent_info}")
            return

        logger.info(f"processing torrent: {torrent_name}")

        properties = self._get_torrent_properties(torrent_hash)
        if not properties:
            logger.warning(
                f"skipping torrent '{torrent_name}' due to error fetching properties."
            )
            return

        files = self._get_torrent_files(torrent_hash)
        if not files:
            logger.warning(
                f"skipping torrent '{torrent_name}' due to error fetching file list."
            )
            return

        sanitized_name = sanitize_filename(torrent_name)
        torrent_out_dir = self.output_dir / sanitized_name

        success_count = 0
        fail_count = 0
        for f in files:
            file_name = f.get("name")
            if not file_name:
                logger.warning(
                    f"torrent '{torrent_name}' has file info missing 'name': {f}"
                )
                fail_count += 1
                continue

            src_path = self._calculate_local_src_path(properties, f)
            if not src_path:
                logger.error(
                    f"could not determine local source path for file '{file_name}' in torrent '{torrent_name}'. skipping file."
                )
                fail_count += 1
                continue

            relative_file_path = Path(file_name)
            dst_path = torrent_out_dir / relative_file_path

            if self._link_or_copy_file(src_path, dst_path):
                success_count += 1
            else:
                fail_count += 1

        if fail_count > 0:
            logger.warning(
                f"finished processing '{torrent_name}' with {success_count} successful links/copies and {fail_count} failures."
            )
        else:
            logger.info(
                f"successfully processed '{torrent_name}' ({success_count} files)."
            )

    def sync_torrents(self) -> None:
        """main sync logic: find completed torrents and process them."""
        logger.info("starting sync run...")
        try:
            all_completed = self.client.torrents(
                filter="completed", get_torrent_generic_properties=False
            )
            logger.info(f"found {len(all_completed)} completed torrents.")
        except Exception as e:
            logger.exception(f"unexpected error retrieving torrent list: {e}")
            return  # exit the function, main will exit

        processed_count = 0
        for torrent in all_completed:
            if self._is_desired_torrent(torrent):
                self.process_torrent(torrent)
                processed_count += 1
            else:
                logger.debug(
                    f"skipping torrent '{torrent.get('name', 'unknown')}' as it doesn't match desired trackers."
                )

        logger.info(
            f"sync run finished. processed {processed_count} matching torrents."
        )


def main():
    logger.info("qbit-sync starting up for a single run...")

    if config["qbit_save_path_prefix"] == config["local_input_dir"]:
        logger.warning(
            f"qbit_save_path_prefix ({config['qbit_save_path_prefix']}) and "
            f"local_input_dir ({config['local_input_dir']}) are identical. "
            "this might be okay, but often indicates misconfiguration."
        )

    exit_code = 0
    qbit_client = connect_client()

    if not qbit_client:
        logger.critical("failed to establish connection to qbittorrent. exiting.")
        exit_code = 1
    else:
        try:
            syncer = QbitSync(qbit_client, config)
            syncer.sync_torrents()
            logger.info("qbit-sync run complete.")
        except Exception as e:
            logger.exception(
                f"an unexpected error occurred during the sync process: {e}"
            )
            exit_code = 1
        # no finally needed here as we exit below

    logger.info("qbit-sync finished.")
    sys.exit(exit_code)


# --- main execution ---
if __name__ == "__main__":
    main()
