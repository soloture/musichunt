# Music Hunt

A daily, non-algorithmic music discovery pipeline for DJ crate-digging.
Every day it researches labels and artists across four source types, writes
up why each one is worth your time, and publishes a page with Bandcamp
players (or a purchase/listen link) so you can vet finds fast.

**Site:** enable GitHub Pages (Settings → Pages → Deploy from branch → `main`
/ `/docs`) once this is merged to `main`; it'll be served at
`https://soloture.github.io/musichunt/`.

## How it works

1. **Seeds** (`seeds/labels.json`, `seeds/artists.json`) are the watch list:
   labels you follow, plus artists pulled from your Rekordbox library.
2. Each day, a research pass works through four source types — see
   `RUNBOOK.md` for the full playbook:
   - **Label watch** — new releases from labels in `seeds/labels.json`.
   - **From your sets** — new work from artists in `seeds/artists.json`.
   - **Associated** — roster mates, remixers, collaborators of recent picks.
   - **Similar** — "labels like X" / "artists like Y" / fans-also-like.
3. Picks are written to `docs/data/YYYY-MM-DD.json`, seeds get topped up with
   anything newly discovered, and `scripts/build_site.py` renders the static
   HTML in `docs/`.
4. Changes are committed straight to `main` and GitHub Pages serves the
   result.

This is driven by a Claude Code Routine that fires daily, reads
`RUNBOOK.md`, does the actual research (web search + fetches against
Bandcamp/RA/label sites/Instagram), and publishes — there's no scraper
infra to maintain, and no API keys required.

## Importing your Rekordbox library

1. In Rekordbox: File → Export Collection in xml format.
2. Run:
   ```
   python3 scripts/parse_rekordbox.py path/to/rekordbox.xml
   ```
   This populates `seeds/artists.json` (and tops up `seeds/labels.json`)
   from the `Artist`, `Remixer`, and `Label` fields on every track in your
   collection. Safe to re-run any time you export a fresh copy — it merges
   rather than overwrites.

## Adding labels/artists by hand

Just add entries to `seeds/labels.json` / `seeds/artists.json` — schema is in
`seeds/SCHEMA.md`. Only `name` is required.

## Resolving a Bandcamp embed manually

```
python3 scripts/bandcamp_lookup.py https://label.bandcamp.com/album/xyz
```
Prints the iframe embed info used in `docs/data/*.json` entries.

## Rebuilding the site after editing data by hand

```
python3 scripts/build_site.py
```
Regenerates `docs/index.html` and `docs/days/*.html` from everything in
`docs/data/`. Pure stdlib, no dependencies.

## Project layout

```
RUNBOOK.md            daily research playbook (source of truth for the routine)
seeds/labels.json      label watch list
seeds/artists.json     artist watch list (Rekordbox-seeded)
seeds/SCHEMA.md         field docs for seeds and daily pick JSON
scripts/parse_rekordbox.py   Rekordbox XML -> seeds/artists.json
scripts/bandcamp_lookup.py   Bandcamp URL -> embeddable player id
scripts/build_site.py        docs/data/*.json -> static docs/ site
docs/data/YYYY-MM-DD.json    one file per day's picks (source of truth for content)
docs/days/YYYY-MM-DD.html    generated daily page
docs/index.html              generated home page (today + archive)
docs/assets/style.css        site styling
```
