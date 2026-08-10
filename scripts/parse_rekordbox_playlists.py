#!/usr/bin/env python3
"""Parse Rekordbox playlist track-list exports (txt, UTF-16, tab-delimited)
into seeds/artists.json.

This is the "Export a playlist as track list" format from Rekordbox
(right-click a playlist > Export track list), distinct from the full
Collection XML export. Columns: #, Artwork, Track Title, Artist, Album,
Genre, BPM, Rating, Time, Key, Date Added. There's no Label column in this
format, so labels aren't extracted here -- use parse_rekordbox.py against a
full XML collection export for that, or add labels manually.

Usage:
    python3 scripts/parse_rekordbox_playlists.py path/to/playlist1.txt [more...]

The playlist name is taken from each file's basename (minus extension),
stripping a leading upload hash prefix like "2a6ddfef-" if present, and
recorded per-artist so the daily hunt has mood/set context to work with.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTISTS_PATH = REPO_ROOT / "seeds" / "artists.json"

UPLOAD_PREFIX_RE = re.compile(r"^[0-9a-f]{8}-", re.IGNORECASE)


def load_json(path):
    if path.exists() and path.read_text().strip():
        return json.loads(path.read_text())
    return []


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def playlist_name(path):
    stem = path.stem
    return UPLOAD_PREFIX_RE.sub("", stem)


def parse_file(path):
    """Yields (artist, genre) tuples for each track row in the file."""
    raw = path.read_bytes()
    text = raw.decode("utf-16")
    lines = [l for l in text.splitlines() if l.strip()]
    if not lines:
        return
    header = lines[0].split("\t")
    try:
        artist_idx = header.index("Artist")
        genre_idx = header.index("Genre")
    except ValueError:
        raise ValueError(f"{path.name}: unexpected header {header!r}")

    for line in lines[1:]:
        cols = line.split("\t")
        if len(cols) <= max(artist_idx, genre_idx):
            continue
        artist = cols[artist_idx].strip()
        genre = cols[genre_idx].strip()
        if artist:
            yield artist, genre


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_rekordbox_playlists.py <playlist.txt> [more.txt ...]")
        sys.exit(1)

    existing = {a["name"]: a for a in load_json(ARTISTS_PATH)}
    seen_this_run = {}

    for arg in sys.argv[1:]:
        path = Path(arg)
        pname = playlist_name(path)
        for artist, genre in parse_file(path):
            entry = seen_this_run.setdefault(
                artist, {"name": artist, "genres": set(), "playlists": set(), "track_count": 0}
            )
            entry["track_count"] += 1
            if genre:
                entry["genres"].add(genre)
            entry["playlists"].add(pname)

    for name, entry in seen_this_run.items():
        merged = existing.get(name, {"name": name})
        merged["source"] = merged.get("source", "rekordbox")
        merged["genres"] = sorted(set(merged.get("genres", [])) | entry["genres"])
        merged["playlists"] = sorted(set(merged.get("playlists", [])) | entry["playlists"])
        merged["track_count"] = merged.get("track_count", 0) + entry["track_count"]
        merged.setdefault("labels", [])
        existing[name] = merged

    save_json(ARTISTS_PATH, sorted(existing.values(), key=lambda a: a["name"].lower()))
    print(f"Parsed {len(seen_this_run)} unique artists from {len(sys.argv) - 1} playlist file(s)")
    print(f"Wrote {ARTISTS_PATH.relative_to(REPO_ROOT)} ({len(existing)} artists total)")


if __name__ == "__main__":
    main()
