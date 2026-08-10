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

**Use WebSearch only — do not use WebFetch, curl, or `bandcamp_lookup.py` to
fetch pages directly.** This environment's network egress is locked down to a
narrow allowlist; direct requests to bandcamp.com, ra.co, instagram.com, and
most label/artist sites are blocked at the proxy (confirmed: `curl` and
WebFetch both fail with `EGRESS_BLOCKED`/403 against these domains — this is
an org-level policy, not a transient error, so don't retry it). WebSearch
works fine and its result snippets are consistently enough to get an artist
bio, release date, label affiliation, and the canonical Bandcamp/RA/website
URL to link to. Do all research through WebSearch; never block on a direct
fetch.

## 2. Curate

**This is a new-release feed, not an artist directory.** Every pick must be
anchored to one specific, named, dated release (album/EP/single/track) that
you can point to. "This artist is worth knowing" is not a pick on its own —
if a candidate from source C or D (associated/similar) doesn't have a
concrete recent release you can name, either keep digging for one or drop
the candidate. Don't pad the day with bio-only entries.

- Bias toward recent finds (rough guideline: released in the last ~60 days),
  but a deeper cut is fine if it's a genuinely new discovery for the seed
  pool — the release still has to be real and datable, just not necessarily
  brand new.
- Skip anything already present in `docs/data/*.json` (match by name).
- Mix across the four source types and across subgenres — don't let one
  label or sound dominate a single day.
- Quality bar: something the DJ would actually cue up, or a clear taste-fit
  based on the seed data.

## 3. Write each pick

Follow the schema in `seeds/SCHEMA.md`. In particular:

- `release`: required for every pick — `title`, `release_type`, and a
  best-confirmed `date`. This is what makes it a "new release" and not just
  an artist recommendation; don't write a pick without one.
- `bio`: 2-3 sentences — who they are, label/scene history. Neutral, factual,
  no invented biographical details — if you're not sure of a fact, leave it
  out rather than guess.
- `why_listen`: 1-2 sentences, DJ-relevant — sound/energy/how it'd fit in a
  set. This is the pitch, keep it sharp.
- `source_note`: one line making the connection concrete, e.g. "Remix collab
  with Peverelist, already in your sets" or "Fans-also-like from Livity
  Sound."
- `bandcamp_embed`: leave this `null`. Resolving it requires fetching the
  Bandcamp page directly (`scripts/bandcamp_lookup.py`), which doesn't work
  from inside this environment (see the egress note above) — it's kept in
  the repo for the DJ to run from their own machine if they want to backfill
  embeds later. Always populate `links.bandcamp` (or `purchase_link`) with
  the direct URL from a WebSearch result instead — that's the reliable path
  and the site already renders a "Buy / Listen" button from it when there's
  no embed.

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
