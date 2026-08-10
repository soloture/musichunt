# Music Hunt — Daily Runbook

This is the playbook the daily research routine follows. It produces 5-8
picks a day (artists or labels) worth checking out, each with a fast way to
listen, published as a static page under `docs/`.

## 0. Orient

- Pull the latest `main`.
- Read `seeds/labels.json` and `seeds/artists.json` — these are the watch
  lists. `artists.json` is seeded from the DJ's Rekordbox library
  (`scripts/parse_rekordbox.py`); `labels.json` starts manual/empty and grows
  as the hunt discovers new labels.
- Skim the last ~14 files in `docs/data/*.json` so you don't repeat a pick.

If both seed files are still empty and no Rekordbox export has been
processed, don't stall — do a best-effort day using open web search for
well-regarded labels/artists in genres the DJ is known to play (check past
`docs/data/*.json` for a genre signal), and say so in the day's summary.

## 1. Gather candidates from four source types

Aim for at least one pick per type per day where possible, but never force a
weak pick just to hit a quota — fewer good picks beats more filler.

**A. Label watch** — rotate through a few labels in `seeds/labels.json`.
Check their Bandcamp label page and Instagram for releases roughly within the
last 30 days that haven't been covered yet.

**B. DJ-set artists** — from `seeds/artists.json`. Check for new releases,
remixes, or side-projects from artists already in the DJ's sets.

**C. Associated new label/artists** — for anything picked today or recently,
look at roster mates, remixers, collaborators, or label alumni that aren't
yet in the seeds. This is how the seed pool grows over time — add newly
found labels/artists into `seeds/*.json`.

**D. Similar labels/artists** — for a label/artist already known-liked,
search "labels like X", "artists similar to Y", Bandcamp's "fans also like",
RA's related-artists, genre-adjacent recommendation lists/blogs.

Use web search and page fetches freely. Prefer primary sources: Bandcamp,
Resident Advisor, label sites, artist Instagram bios/posts. Instagram's own
search/API access is unreliable for automation — treat it as a place to
*verify* an artist/label's current activity via their public profile page,
not a primary crawling target.

## 2. Curate

- Bias toward recent finds (rough guideline: released/active in the last ~60
  days), but a deeper cut is fine if it's a genuinely new discovery for the
  seed pool.
- Skip anything already present in `docs/data/*.json` (match by name).
- Mix across the four source types and across subgenres — don't let one
  label or sound dominate a single day.
- Quality bar: something the DJ would actually cue up, or a clear taste-fit
  based on the seed data.

## 3. Write each pick

Follow the schema in `seeds/SCHEMA.md`. In particular:

- `bio`: 2-3 sentences — who they are, label/scene history. Neutral, factual,
  no invented biographical details — if you're not sure of a fact, leave it
  out rather than guess.
- `why_listen`: 1-2 sentences, DJ-relevant — sound/energy/how it'd fit in a
  set. This is the pitch, keep it sharp.
- `source_note`: one line making the connection concrete, e.g. "Remix collab
  with Peverelist, already in your sets" or "Fans-also-like from Livity
  Sound."
- `bandcamp_embed`: if there's a Bandcamp link, resolve it with
  `python3 scripts/bandcamp_lookup.py <url>` and use the returned
  `iframe_src`. If that fails or there's no Bandcamp page, leave it `null`
  and make sure `links`/`purchase_link` gives a fast way to listen elsewhere
  (RA, artist site, etc).

## 4. Publish

1. Write `docs/data/YYYY-MM-DD.json` (today's date) with the day's picks.
2. Update `seeds/labels.json` / `seeds/artists.json` with any newly
   discovered labels/artists (dedup by `name`; don't clobber existing
   manually-added fields).
3. Run `python3 scripts/build_site.py` — regenerates `docs/index.html` and
   `docs/days/YYYY-MM-DD.html`.
4. Commit and push directly to `main`
   (`git add seeds docs && git commit -m "Music hunt: YYYY-MM-DD" && git push`).
   This site is low-stakes personal content, not production code — no PR
   needed for the daily run.

## 5. Notify

Send a short push notification / message: a one-line summary of the day's
picks and the GitHub Pages link.
