#!/usr/bin/env python3

import os
import random
import pathlib
import urllib.parse
import requests
import sys
import re
import google.generativeai as genai

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


# Function to get review from Gemini - ADDED
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
            generation_config=genai.types.GenerationConfig(
                # adjust temp/top_p etc. if you want more/less chaotic reviews
                temperature=0.75
            ),
            # add safety_settings if needed
        )

        # basic check if response has text part
        if response.parts:
            # Check for empty text part which can happen
            if hasattr(response.parts[0], "text") and response.parts[0].text:
                return response.text.strip()
            else:
                # If blocked due to safety or other reasons without text
                block_reason = (
                    response.prompt_feedback.block_reason
                    if response.prompt_feedback
                    else "unknown reason"
                )
                return f"(review generation blocked/empty: {block_reason})"
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
            # Handle cases where the prompt itself was blocked
            return f"(review prompt blocked: {response.prompt_feedback.block_reason})"
        else:
            # Fallback for unexpected empty response
            return "(review generation failed: empty response)"

    except Exception as e:
        # Catch other potential api errors
        print(f"gemini api call failed for {rel_path_str}: {e}", file=sys.stderr)
        return f"(review generation failed: {type(e).__name__})"


# --- Main Message Construction ---
lines = ["📚 **random picks rn (w/ ai reviews)**"]  # updated header
for p in chosen:
    rel_path = p.relative_to(ROOT_DIR)
    rel_path_str = str(rel_path)
    file_link = f"<{file_url(p)}>"

    # Use filename stem as a basic title guess, could be improved
    title_guess = p.stem

    # --- Get Gemini Review ---
    print(f"getting gemini review for {rel_path_str}", file=sys.stderr)
    review_text = get_gemini_review(rel_path_str)
    # ---

    # Format: Title (link) newline > review
    lines.append(f"- **{title_guess}** {file_link}\n  > {review_text}")

payload = {"content": "\n".join(lines)}
print(payload)
print(f"posting {len(chosen)} files + reviews to webhook", file=sys.stderr)
resp = requests.post(WEBHOOK, json=payload, timeout=15)
resp.raise_for_status()
print(f"sent ok - webhook responded {resp.status_code}", file=sys.stderr)
