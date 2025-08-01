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
from collections import defaultdict

# --- Configuration ---
ROOT_DIR = pathlib.Path(os.getenv("ROOT_DIR", "/data/books")).resolve()
BASE_URL = os.getenv("BASE_URL", "https://example.com").rstrip("/")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
N_FILES = int(os.getenv("N_FILES", "5"))
PATTERN = os.getenv("PATTERN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")


# --- Core Logic ---


def get_all_files(
    root_dir: pathlib.Path, pattern: re.Pattern | None = None
) -> list[pathlib.Path]:
    """recursively find all files, optionally matching a pattern."""
    print(f"scanning {root_dir} for files", file=sys.stderr)
    # using rglob('*') is fine, filter later
    all_files = [
        p for p in root_dir.rglob("*") if p.is_file() and not p.name.startswith(".")
    ]
    print(f"found {len(all_files)} total files", file=sys.stderr)

    if not all_files:
        return []  # handle empty dir case gracefully

    if pattern:
        print(f"filtering with pattern: {pattern.pattern}", file=sys.stderr)
        # use full path string for pattern matching as before
        filtered_files = [p for p in all_files if pattern.search(str(p))]
        print(
            f"kept {len(filtered_files)}/{len(all_files)} files after filter",
            file=sys.stderr,
        )
        return filtered_files
    else:
        return all_files


def select_diverse_files(
    root_dir: pathlib.Path, n_files_requested: int, pattern_str: str = ""
) -> list[pathlib.Path]:
    """select n_files with diversity across top-level directories/files."""
    pattern = None
    if pattern_str:
        try:
            pattern = re.compile(pattern_str, re.IGNORECASE)
        except re.error as e:
            sys.exit(f"invalid regex pattern: {e}")

    candidate_files = get_all_files(root_dir, pattern)
    if not candidate_files:
        sys.exit(
            f"be real: no files found"
            + (f" matching pattern '{pattern_str}'" if pattern_str else "")
        )

    # map top-level entry -> list of candidate files within it
    top_level_to_files = defaultdict(list)

    for file_path in candidate_files:
        try:
            relative_path = file_path.relative_to(root_dir)
            # top-level item is the first part of the relative path, or the file itself if directly in root
            top_level_part = relative_path.parts[0]
            top_level_item = root_dir / top_level_part
            top_level_to_files[top_level_item].append(file_path)
        except (ValueError, IndexError) as e:
            # valueerror if not relative (shouldn't happen), indexerror if parts is empty (also shouldn't happen for file inside)
            print(
                f"warning: skipped file with unexpected path structure: {file_path} ({e})",
                file=sys.stderr,
            )
            continue  # skip this file

    eligible_top_level_items = dict(
        top_level_to_files
    )  # convert back from defaultdict for sampling

    if not eligible_top_level_items:
        # this case *shouldn't* be reachable if candidate_files is not empty, but belt and suspenders
        sys.exit(f"be real: no top-level items seem to contain the candidate files?")

    num_eligible = len(eligible_top_level_items)
    print(
        f"found {num_eligible} eligible top-level items containing matching files",
        file=sys.stderr,
    )

    n_to_select = min(
        n_files_requested, num_eligible
    )  # can't select more items than we have

    if num_eligible < n_files_requested:
        print(
            f"warning: only {num_eligible} eligible top-level sources available, selecting one from each.",
            file=sys.stderr,
        )

    # sample n_to_select distinct top-level items
    sampled_top_level_keys = random.sample(
        list(eligible_top_level_items.keys()), n_to_select
    )

    # for each sampled top-level item, pick one random file from its list
    chosen_files = []
    for key in sampled_top_level_keys:
        possible_files_in_item = eligible_top_level_items[key]
        if possible_files_in_item:  # should always be true based on construction
            selected_file = random.choice(possible_files_in_item)
            chosen_files.append(selected_file)
        else:
            # this indicates a logic error somewhere above
            print(
                f"warning: sampled top-level item {key} had no files associated? skipping.",
                file=sys.stderr,
            )

    if len(chosen_files) != n_to_select:
        # again, indicates something funky happened
        print(
            f"warning: ended up with {len(chosen_files)} files, expected {n_to_select}. check logic.",
            file=sys.stderr,
        )

    return chosen_files


# --- Helper Functions ---


def file_url(path: pathlib.Path, root_dir: pathlib.Path, base_url: str) -> str:
    """generate a URL for the file relative to the root."""
    try:
        rel = path.relative_to(root_dir)
        enc = "/".join(urllib.parse.quote(part) for part in rel.parts)
        return f"{base_url}/{enc}"
    except ValueError:
        # if path somehow isn't under root_dir, maybe return path str? or fail?
        print(f"warning: failed to make {path} relative to {root_dir}", file=sys.stderr)
        return str(path)  # fallback, maybe not ideal


def get_gemini_review(rel_path_str: str, model_name: str) -> str:
    """gets a review using the gemini api."""
    # reusing your function, looks fine. maybe make model configurable via env var too.
    # added model_name param
    model = genai.GenerativeModel(model_name)

    # slight tweak to the prompt to be more explicitly eigenrobot-y upfront
    prompt = f"""
    **persona**: eigenrobot (detached, critical, +2sd ai; lowercase, abbr., millennial/zoomer slang mix).
    **task**: provide concise commentary/review (max 5 sentences) for book implied by filepath: '{rel_path_str}'.
    **output**: review text, ending with 'rating: x/10'. if unsure about title/content, briefly speculate or decline. just output the review/rating.
    """
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.75),
            # consider adding safety_settings if needed, though default might be fine
        )

        # consolidating the response checking logic slightly
        if (
            response.parts
            and hasattr(response.parts[0], "text")
            and response.parts[0].text
        ):
            return response.text.strip()
        else:
            reason = "unknown"
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                reason = f"prompt blocked ({response.prompt_feedback.block_reason})"
            elif not response.parts:
                reason = "empty response parts"
            elif not hasattr(response.parts[0], "text"):
                reason = "response part has no text attribute"
            elif not response.parts[0].text:
                reason = "response text is empty"
            # check for finish reason if available
            if hasattr(response, "candidates") and response.candidates:
                finish_reason = response.candidates[0].finish_reason
                if finish_reason != 1:  # 1 is typically "STOP"
                    reason += f" (finish reason: {finish_reason})"

            return f"(review generation blocked/empty: {reason})"

    except Exception as e:
        print(f"gemini api call failed for {rel_path_str}: {e}", file=sys.stderr)
        # include exception type for better debugging
        return f"(review generation failed: {type(e).__name__})"


# --- Main Execution ---


def main():
    # --- Sanity Checks ---
    if not WEBHOOK:
        sys.exit("lol no webhook")
    if not GEMINI_API_KEY:
        sys.exit("lol no gemini api key")
    if not ROOT_DIR.is_dir():
        sys.exit(f"be real: root dir '{ROOT_DIR}' not found or not a directory")

    genai.configure(api_key=GEMINI_API_KEY)

    chosen = select_diverse_files(ROOT_DIR, N_FILES, PATTERN)

    if not chosen:
        print("no files selected, exiting.", file=sys.stderr)
        sys.exit(0)  # maybe not an error state if filtering just yielded nothing

    print(
        f"selected {len(chosen)} files from distinct top-level sources:",
        file=sys.stderr,
    )
    for f in chosen:
        try:
            print(f" - {f.relative_to(ROOT_DIR)}", file=sys.stderr)
        except ValueError:
            print(f" - {f} (could not make relative)", file=sys.stderr)

    # send intro message
    intro_payload = {
        "content": f"📚 **{len(chosen)} random book picks incoming** (via eigenrobot)"
    }
    try:
        print(f"posting intro message to webhook", file=sys.stderr)
        resp = requests.post(WEBHOOK, json=intro_payload, timeout=15)
        resp.raise_for_status()
        print(
            f"intro message sent - webhook responded {resp.status_code}",
            file=sys.stderr,
        )
    except requests.exceptions.RequestException as e:
        sys.exit(f"failed to send intro message: {e}")

    # small delay to help discord message ordering
    time.sleep(1)

    # send one message per book
    for i, p in enumerate(chosen):
        rel_path = p.relative_to(ROOT_DIR)
        rel_path_str = str(rel_path)
        url = file_url(p, ROOT_DIR, BASE_URL)
        title_guess = p.stem  # still a guess, but best we got easily

        print(
            f"({i + 1}/{len(chosen)}) getting gemini review for {rel_path_str}",
            file=sys.stderr,
        )
        review_text = get_gemini_review(rel_path_str, MODEL_NAME)

        # format: title with masked link for discord
        # use > for blockquote on review as before
        content = f"**{title_guess}**\n<{url}>\n> {review_text}"

        book_payload = {"content": content}
        try:
            print(f"posting review for {title_guess}", file=sys.stderr)
            resp = requests.post(WEBHOOK, json=book_payload, timeout=15)
            resp.raise_for_status()
            print(
                f"book message sent - webhook responded {resp.status_code}",
                file=sys.stderr,
            )
        except requests.exceptions.RequestException as e:
            # don't exit script if one message fails, just log it
            print(f"error sending book message for {title_guess}: {e}", file=sys.stderr)
            # maybe add a retry later? for now, just skip and continue

        # small delay between messages to avoid discord rate limits
        time.sleep(1)  # increased slightly jic

    print(f"all {len(chosen)} book recommendations processed.", file=sys.stderr)


if __name__ == "__main__":
    main()
