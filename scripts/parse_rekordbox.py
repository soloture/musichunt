#!/usr/bin/env python3
"""Parse a Rekordbox XML library export into seeds/artists.json (and
top up seeds/labels.json with labels seen on those tracks).

Export from Rekordbox: File > Export Collection in xml format.

Usage:
    python3 scripts/parse_rekordbox.py path/to/rekordbox.xml
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ARTISTS_PATH = REPO_ROOT / "seeds" / "artists.json"
LABELS_PATH = REPO_ROOT / "seeds" / "labels.json"

IGNORED_LABELS = {"", "various", "various artists", "unknown", "n/a"}


def load_json(path):
    if path.exists() and path.read_text().strip():
        return json.loads(path.read_text())
    return []


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: parse_rekordbox.py <rekordbox_export.xml>")
        sys.exit(1)

    xml_path = Path(sys.argv[1])
    root = ET.parse(xml_path).getroot()

    artists = {}
    labels = {}

    for track in root.iter("TRACK"):
        artist = (track.get("Artist") or "").strip()
        remixer = (track.get("Remixer") or "").strip()
        label = (track.get("Label") or "").strip()
        genre = (track.get("Genre") or "").strip()

        for name in filter(None, [artist, remixer]):
            entry = artists.setdefault(
                name, {"name": name, "genres": set(), "labels": set(), "track_count": 0}
            )
            entry["track_count"] += 1
            if genre:
                entry["genres"].add(genre)
            if label and label.lower() not in IGNORED_LABELS:
                entry["labels"].add(label)

        if label and label.lower() not in IGNORED_LABELS:
            lentry = labels.setdefault(label, {"name": label, "track_count": 0})
            lentry["track_count"] += 1

    existing_artists = {a["name"]: a for a in load_json(ARTISTS_PATH)}
    existing_labels = {l["name"]: l for l in load_json(LABELS_PATH)}

    for name, entry in artists.items():
        merged = existing_artists.get(name, {"name": name})
        merged["source"] = merged.get("source", "rekordbox")
        merged["genres"] = sorted(set(merged.get("genres", [])) | entry["genres"])
        merged["labels"] = sorted(set(merged.get("labels", [])) | entry["labels"])
        merged["track_count"] = entry["track_count"]
        existing_artists[name] = merged

    for name, entry in labels.items():
        merged = existing_labels.get(name, {"name": name})
        merged["source"] = merged.get("source", "rekordbox")
        merged["track_count"] = entry["track_count"]
        existing_labels[name] = merged

    save_json(ARTISTS_PATH, sorted(existing_artists.values(), key=lambda a: a["name"].lower()))
    save_json(LABELS_PATH, sorted(existing_labels.values(), key=lambda l: l["name"].lower()))

    print(f"Parsed {len(artists)} artists and {len(labels)} labels from {xml_path.name}")
    print(f"Wrote {ARTISTS_PATH.relative_to(REPO_ROOT)} and {LABELS_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
