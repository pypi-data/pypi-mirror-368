#!/usr/bin/env python3
"""
markitdown_cli_wrapper.py

Lightweight CLI wrapper around Microsoft's `markitdown` Python API.
Usage:
  pip install markitdown requests beautifulsoup4
  python3 markitdown_cli_wrapper.py https://collabfund.com/blog/the-dumber-side-of-smart-people/

Behavior:
- Extracts a sensible default slug/title from the URL path (falls back to HTML <title>).
- Prompts the user with the suggested title; press Enter to accept or type a custom title.
- Converts the page to Markdown using markitdown and writes `<title>.md` (hyphenated, sanitized).

Designed as a single-file, dependency-light CLI for batch scripting or manual use.
"""

from __future__ import annotations
import argparse
import os
import re
import sys
import tempfile
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

try:
    from markitdown import MarkItDown
except Exception as e:
    print("ERROR: failed to import markitdown. Install with: pip install markitdown")
    raise


def slugify(text: str) -> str:
    if not text:
        return "untitled"
    text = text.strip().lower()
    # replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # remove characters that are not alphanumeric or hyphen
    text = re.sub(r"[^a-z0-9-]", "", text)
    # collapse multiple hyphens
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "untitled"


def title_from_url_path(url: str) -> str | None:
    p = urlparse(url)
    segments = [s for s in p.path.split("/") if s]
    if not segments:
        return None
    return slugify(segments[-1])


def title_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    t = None
    if soup.title and soup.title.string:
        t = soup.title.string.strip()
    if not t:
        # try meta og:title
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            t = og.get("content").strip()
    if not t:
        return None
    return slugify(t)


def fetch_url_to_tempfile(url: str) -> str:
    headers = {"User-Agent": "markitdown-wrapper/1.0 (+https://github.com)"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    suffix = ".html"
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def ask_title(default: str) -> str:
    prompt = f"Suggested title [{default}]: "
    try:
        user = input(prompt)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    if not user.strip():
        return default
    return slugify(user)


def convert_with_markitdown(file_path: str) -> str:
    md = MarkItDown(enable_plugins=False)
    result = md.convert(file_path)
    # MarkItDown returns an object — docs show `text_content` attribute
    text = getattr(result, "text_content", None)
    if text is None:
        # try `result.text` or string conversion
        text = getattr(result, "text", None)
    if text is None:
        text = str(result)
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description="Small CLI wrapper for markitdown: URL -> markdown file with interactive title.")
    ap.add_argument("url", help="URL to convert")
    ap.add_argument("-o", "--outdir", default=".", help="Output directory (default: current dir)")
    ap.add_argument("--keep-temp", action="store_true", help="Keep temp file (for debugging)")
    args = ap.parse_args()

    url = args.url
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    # 1) try to get slug from URL path
    default_title = title_from_url_path(url) or "untitled"

    # 2) if slug is trivial, try fetching HTML title
    if default_title in (None, "untitled"):
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            html_title = title_from_html(r.text)
            if html_title:
                default_title = html_title
        except Exception:
            # ignore — we'll prompt user
            pass

    # Prompt user
    chosen = ask_title(default_title)
    out_fname = f"{chosen}.md"
    out_path = os.path.join(outdir, out_fname)

    # 3) fetch and save to temp file
    try:
        tmp_path = fetch_url_to_tempfile(url)
    except Exception as e:
        print(f"Failed to fetch URL: {e}")
        sys.exit(2)

    # 4) convert using markitdown
    try:
        md_text = convert_with_markitdown(tmp_path)
    except Exception as e:
        print(f"Conversion failed: {e}")
        if not args.keep_temp and os.path.exists(tmp_path):
            os.remove(tmp_path)
        sys.exit(3)

    # 5) write output
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    if not args.keep_temp:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
