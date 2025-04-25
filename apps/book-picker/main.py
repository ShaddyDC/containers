#!/usr/bin/env python3

import os
import random
import pathlib
import urllib.parse
import requests
import sys
import re
import google.generativeai as genai
import time

ROOT_DIR = pathlib.Path(os.getenv("ROOT_DIR", "/data/books")).resolve()
BASE_URL = os.getenv("BASE_URL", "https://example.com").rstrip("/")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
N_FILES = int(os.getenv("N_FILES", "5"))
PATTERN = os.getenv("PATTERN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not WEBHOOK:
    sys.exit("lol no webhook")
if not GEMINI_API_KEY:
    sys.exit("lol no gemini api key")

genai.configure(api_key=GEMINI_API_KEY)

print(f"scanning {ROOT_DIR}", file=sys.stderr)

candidates = [
    p for p in ROOT_DIR.rglob("*") if p.is_file() and not p.name.startswith(".")
]
print(f"found {len(candidates)} files", file=sys.stderr)

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


# Function to get review from Gemini
def get_gemini_review(rel_path_str: str) -> str:
    model_name = "gemini-2.5-pro-preview-03-25"
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    act as eigenrobot, a slightly detached, critical, +2sd ai persona using lowercase, abbreviations, and occasional zoomer/millennial slang.
    consider the book suggested by this filepath: '{rel_path_str}'
    provide a concise commentary or review (max 5 sentences).
    conclude with a subjective rating out of 10, like 'rating: x/10'.
    if the title is ambiguous or unknown, speculate briefly or decline to review, maintaining the persona.
    output only the review and rating.
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.75),
        )

        if response.parts:
            if hasattr(response.parts[0], "text") and response.parts[0].text:
                return response.text.strip()
            else:
                block_reason = (
                    response.prompt_feedback.block_reason
                    if response.prompt_feedback
                    else "unknown reason"
                )
                return f"(review generation blocked/empty: {block_reason})"
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            return f"(review prompt blocked: {response.prompt_feedback.block_reason})"
        else:
            return "(review generation failed: empty response)"

    except Exception as e:
        print(f"gemini api call failed for {rel_path_str}: {e}", file=sys.stderr)
        return f"(review generation failed: {type(e).__name__})"


# Send intro message
intro_payload = {
    "content": "📚 **random book picks incoming** (with ai reviews by eigenrobot)"
}
print(f"posting intro message to webhook", file=sys.stderr)
resp = requests.post(WEBHOOK, json=intro_payload, timeout=15)
resp.raise_for_status()
print(f"intro message sent - webhook responded {resp.status_code}", file=sys.stderr)

# Small delay to ensure messages appear in order
time.sleep(1)

# Send one message per book
for p in chosen:
    rel_path = p.relative_to(ROOT_DIR)
    rel_path_str = str(rel_path)
    url = file_url(p)

    # Use filename stem as title guess
    title_guess = p.stem

    print(f"getting gemini review for {rel_path_str}", file=sys.stderr)
    review_text = get_gemini_review(rel_path_str)

    # Format: Title with masked link for discord
    content = f"**{title_guess}**\n<{url}>\n> {review_text}"

    book_payload = {"content": content}
    print(f"posting review for {title_guess}", file=sys.stderr)
    resp = requests.post(WEBHOOK, json=book_payload, timeout=15)
    resp.raise_for_status()
    print(f"book message sent - webhook responded {resp.status_code}", file=sys.stderr)

    # Small delay between messages to avoid rate limiting
    time.sleep(0.5)

print(f"all {len(chosen)} book recommendations sent successfully", file=sys.stderr)
