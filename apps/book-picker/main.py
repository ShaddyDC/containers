#!/usr/bin/env python3

import os
import random
import pathlib
import urllib.parse
import requests
import sys
import re

ROOT_DIR = pathlib.Path(os.getenv("ROOT_DIR", "/data/books")).resolve()
BASE_URL = os.getenv("BASE_URL", "https://example.com").rstrip("/")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
N_FILES = int(os.getenv("N_FILES", "5"))
SEARCH = os.getenv("SEARCH_ENGINE", "kagi")  # "kagi" or "google"

# Filter option
PATTERN = os.getenv("PATTERN", "")  # regex pattern to match against full path

if not WEBHOOK:
    sys.exit("lol no webhook")

print(f"scanning {ROOT_DIR}", file=sys.stderr)

# gather all regular (non-hidden) files
candidates = [
    p for p in ROOT_DIR.rglob("*") if p.is_file() and not p.name.startswith(".")
]
print(f"found {len(candidates)} files", file=sys.stderr)

# apply regex pattern filter if specified
if PATTERN:
    try:
        pattern = re.compile(PATTERN, re.IGNORECASE)
        print(f"filtering with pattern: {PATTERN}", file=sys.stderr)
        pre_count = len(candidates)
        candidates = [p for p in candidates if pattern.search(str(p))]
        print(f"kept {len(candidates)}/{pre_count} files after filter", file=sys.stderr)
    except re.error as e:
        sys.exit(f"invalid regex pattern: {e}")

if len(candidates) < N_FILES:
    sys.exit(f"be real: only {len(candidates)} files after filtering")

chosen = random.sample(candidates, N_FILES)


def file_url(path: pathlib.Path) -> str:
    rel = path.relative_to(ROOT_DIR)
    enc = "/".join(urllib.parse.quote(part) for part in rel.parts)
    return f"{BASE_URL}/{enc}"


def search_url(stem: str) -> str:
    q = urllib.parse.quote_plus(f"{stem} goodreads")
    return (
        f"https://kagi.com/search?q={q}"
        if SEARCH == "kagi"
        else f"https://www.google.com/search?q={q}"
    )


lines = [
    "📚 **random picks rn**",
    *(f"- <{file_url(p)}> ▸ <{search_url(p.stem)}>" for p in chosen),
]

payload = {"content": "\n".join(lines)}
print(payload)
print(f"posting {len(chosen)} files to webhook", file=sys.stderr)
resp = requests.post(WEBHOOK, json=payload, timeout=15)
resp.raise_for_status()
print(f"sent ok - webhook responded {resp.status_code}", file=sys.stderr)
