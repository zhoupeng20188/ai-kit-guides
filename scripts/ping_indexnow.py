#!/usr/bin/env python3
"""Local IndexNow pinger for aikitguides.com.

Usage:
  python scripts/ping_indexnow.py                 # submit all NEW urls (vs local cache)
  python scripts/ping_indexnow.py --dry-run       # show what would be submitted, no API call
  python scripts/ping_indexnow.py <url1> <url2>   # submit specific urls directly

The local cache (which urls were already submitted) lives in
~/.cache/aikitguides_indexnow.json so it never enters the git repo.
This script is intentionally NOT committed — keep it local only.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

KEY = "8a834bf69f0b49f8ae8f3d97e0eed0f8"
HOST = "aikitguides.com"
SITEMAP = f"https://{HOST}/sitemap-index.xml"
API = "https://api.indexnow.org/indexnow"
CACHE = Path.home() / ".cache" / "aikitguides_indexnow.json"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "indexnow-ping/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def all_urls():
    xml = fetch(SITEMAP)
    subs = re.findall(r"<loc>(.*?)</loc>", xml)
    urls = []
    for s in subs:
        try:
            urls += re.findall(r"<loc>(.*?)</loc>", fetch(s))
        except Exception as e:
            print(f"  skip {s}: {e}")
    return urls


def load_cache():
    if CACHE.exists():
        try:
            return set(json.loads(CACHE.read_text()))
        except Exception:
            return set()
    return set()


def save_cache(urls):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(sorted(urls)))


def ping(urls, dry=False):
    if dry:
        print(f"[dry-run] would submit {len(urls)} urls:")
        for u in urls:
            print("  ", u)
        return
    body = json.dumps({"host": HOST, "key": KEY, "urlList": urls}).encode()
    req = urllib.request.Request(
        API, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow OK: status {r.status}, submitted {len(urls)} urls")
    except urllib.error.HTTPError as e:
        print(f"IndexNow ERROR {e.code}: {e.read().decode()}")


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    targets = [a for a in args if a != "--dry-run"]

    if targets:
        ping(targets, dry)
        return

    urls = all_urls()
    prev = load_cache()
    new = [u for u in urls if u not in prev]
    if not new:
        print("No new URLs to submit.")
        return
    ping(new, dry)
    if not dry:
        save_cache(urls)


if __name__ == "__main__":
    main()
