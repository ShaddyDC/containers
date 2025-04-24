#!/usr/bin/env python3

import os
import random
import pathlib
import urllib.parse
import requests
import sys

ROOT_DIR = pathlib.Path(os.getenv("ROOT_DIR", "/data/books")).resolve()
BASE_URL = os.getenv("BASE_URL", "https://example.com").rstrip("/")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
N_FILES = int(os.getenv("N_FILES", "5"))
SEARCH = os.getenv("SEARCH_ENGINE", "kagi")  # "kagi" or "google"

if not WEBHOOK:
    sys.exit("lol no webhook")

# gather all regular (non-hidden) files
candidates = [
    p for p in ROOT_DIR.rglob("*") if p.is_file() and not p.name.startswith(".")
]
if len(candidates) < N_FILES:
    sys.exit(f"be real: only {len(candidates)} files")

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
requests.post(WEBHOOK, json=payload, timeout=15).raise_for_status()
print("sent ok", file=sys.stderr)
