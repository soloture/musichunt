#!/usr/bin/env python3
"""Resolve a Bandcamp track/album URL into an embeddable player.

Usage:
    python3 scripts/bandcamp_lookup.py <bandcamp_url>

Prints JSON: {"type": "album"|"track", "id": "...", "iframe_src": "...", "source_url": "..."}
or {"error": "..."} if it couldn't be resolved (e.g. not a Bandcamp track/album page).
"""
import html as htmllib
import json
import re
import sys
import urllib.request

USER_AGENT = "Mozilla/5.0 (compatible; MusicHuntBot/1.0; +https://github.com/soloture/musichunt)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def lookup(url):
    page = fetch(url)

    match = re.search(r'data-tralbum="([^"]+)"', page)
    if not match:
        return {"error": "no Bandcamp track/album data found on page"}

    blob = htmllib.unescape(match.group(1))
    data = json.loads(blob)
    current = data.get("current", {})

    item_id = current.get("id")
    item_type = current.get("type")
    if not item_id:
        return {"error": "no item id found in page data"}

    kind = "album" if item_type == "album" else "track"
    iframe_src = (
        f"https://bandcamp.com/EmbeddedPlayer/{kind}={item_id}/size=large/"
        "bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=small/transparent=true/"
    )
    return {"type": kind, "id": str(item_id), "iframe_src": iframe_src, "source_url": url}


def main():
    if len(sys.argv) != 2:
        print("Usage: bandcamp_lookup.py <bandcamp_url>")
        sys.exit(1)
    try:
        result = lookup(sys.argv[1])
    except Exception as exc:
        result = {"error": str(exc)}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
