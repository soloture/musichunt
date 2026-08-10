# Seed & pick schemas

## `seeds/labels.json`

Array of label objects, deduped by `name`:

```json
{
  "name": "Livity Sound",
  "source": "manual | rekordbox | discovered",
  "genres": ["UK bass", "dub techno"],
  "track_count": 4,
  "links": {
    "bandcamp": "https://livitysound.bandcamp.com",
    "website": "https://livitysound.co.uk",
    "instagram": "https://instagram.com/livitysound",
    "ra": "https://ra.co/labels/xxxx"
  },
  "last_checked": "2026-08-01"
}
```

Only `name` is required. Everything else fills in over time — manually, via the
Rekordbox parser, or via the daily research routine adding labels it discovers.
An optional `notes` string is fine for freeform context (why it's seeded, an
artist connection, "inactive since X" for defunct labels that shouldn't be
watched for new releases).

## `seeds/artists.json`

Same shape as labels, plus `labels` (labels this artist has released on) and
`playlists` (which of your Rekordbox playlists they showed up in -- useful
mood/set-context signal, e.g. `"Bass"`, `"slow"`, `"Bar"`):

```json
{
  "name": "Peverelist",
  "source": "rekordbox",
  "genres": ["dubstep", "techno"],
  "labels": ["Punch Drunk", "Livity Sound"],
  "playlists": ["Bass", "UKHouse"],
  "track_count": 6,
  "links": { "bandcamp": "...", "instagram": "..." },
  "last_checked": "2026-08-01"
}
```

`source: "rekordbox"` entries come from `scripts/parse_rekordbox_playlists.py`
(playlist track-list `.txt` exports -- artist/genre/playlist, no label data)
and/or `scripts/parse_rekordbox.py` (full Collection XML export -- adds
label/remixer data). Both merge rather than overwrite; `track_count` is
regenerated from whatever's re-imported.

## `docs/data/YYYY-MM-DD.json` (one file per daily hunt)

```json
{
  "date": "2026-08-10",
  "picks": [
    {
      "name": "Artist or Label Name",
      "type": "artist",
      "source_type": "label_watch",
      "source_note": "New EP on Livity Sound, a label you've got several tracks from.",
      "genres": ["UK bass", "dub techno"],
      "bio": "2-3 sentences: who they are, scene/label history.",
      "why_listen": "1-2 sentences: DJ-relevant pitch — sound, energy, where it'd fit in a set.",
      "links": {
        "bandcamp": "https://...",
        "website": "https://...",
        "instagram": "https://...",
        "ra": "https://ra.co/..."
      },
      "bandcamp_embed": {
        "type": "album",
        "id": "1234567890",
        "iframe_src": "https://bandcamp.com/EmbeddedPlayer/album=1234567890/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/artwork=small/transparent=true/"
      },
      "purchase_link": null
    }
  ]
}
```

Field notes:
- `type`: `"artist"` or `"label"`.
- `source_type`: one of `label_watch`, `dj_set_artist`, `associated`, `similar` — see `RUNBOOK.md` for what each means.
- `bandcamp_embed`: `null` if there's no Bandcamp page to embed; use `scripts/bandcamp_lookup.py <url>` to resolve it. When null, `purchase_link` or `links` carry the fallback.
