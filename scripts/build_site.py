#!/usr/bin/env python3
"""Regenerate docs/index.html and docs/days/*.html from docs/data/*.json.

Usage: python3 scripts/build_site.py
"""
import html
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "docs" / "data"
DAYS_DIR = REPO_ROOT / "docs" / "days"
INDEX_PATH = REPO_ROOT / "docs" / "index.html"

SITE_TITLE = "Music Hunt"

SOURCE_LABELS = {
    "label_watch": "Label watch",
    "dj_set_artist": "From your sets",
    "associated": "Associated",
    "similar": "Similar",
}

LINK_ORDER = [
    ("bandcamp", "Bandcamp"),
    ("ra", "Resident Advisor"),
    ("website", "Website"),
    ("instagram", "Instagram"),
]


def esc(s):
    return html.escape(s or "", quote=True)


def fmt_date(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%A, %B %-d, %Y")


def load_days():
    days = []
    for path in sorted(DATA_DIR.glob("*.json")):
        days.append(json.loads(path.read_text()))
    days.sort(key=lambda d: d["date"], reverse=True)
    return days


def render_links(links, purchase_link):
    items = []
    for key, label in LINK_ORDER:
        url = links.get(key)
        if url:
            items.append(f'<a class="link-pill" href="{esc(url)}" target="_blank" rel="noopener">{label}</a>')
    if purchase_link and purchase_link not in links.values():
        items.append(
            f'<a class="link-pill link-pill-buy" href="{esc(purchase_link)}" target="_blank" rel="noopener">Buy / Listen</a>'
        )
    return "\n".join(items)


def render_card(pick):
    name = esc(pick.get("name"))
    ptype = (pick.get("type") or "artist").lower()
    source_type = pick.get("source_type", "")
    source_label = esc(SOURCE_LABELS.get(source_type, source_type or "Discovery"))
    source_note = esc(pick.get("source_note", ""))
    genres = pick.get("genres", []) or []
    genre_html = "".join(f'<span class="tag">{esc(g)}</span>' for g in genres)
    bio = esc(pick.get("bio", ""))
    why = esc(pick.get("why_listen", ""))
    links = pick.get("links") or {}
    purchase_link = pick.get("purchase_link")
    embed = pick.get("bandcamp_embed")

    media_html = ""
    if embed and embed.get("iframe_src"):
        media_html = (
            f'<iframe class="bandcamp-embed" style="border: 0; width: 100%; height: 120px;" '
            f'src="{esc(embed["iframe_src"])}" seamless loading="lazy" title="{name} on Bandcamp"></iframe>'
        )

    return f"""
    <article class="card">
      <header class="card-header">
        <span class="type-badge type-{esc(ptype)}">{esc(ptype.upper())}</span>
        <span class="source-badge source-{esc(source_type)}">{source_label}</span>
      </header>
      <h3 class="card-name">{name}</h3>
      {f'<p class="source-note">{source_note}</p>' if source_note else ""}
      <div class="tags">{genre_html}</div>
      <p class="bio">{bio}</p>
      <p class="why-listen"><strong>Why listen:</strong> {why}</p>
      {media_html}
      <div class="links">{render_links(links, purchase_link)}</div>
    </article>
    """


def page_head(title, css_path, home_path):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{css_path}assets/style.css">
</head>
<body>
<div class="page">
<header class="site-header">
  <a class="site-title" href="{home_path}index.html">{SITE_TITLE}</a>
  <nav><a href="{home_path}index.html">Archive</a></nav>
</header>
"""


PAGE_FOOT = """
</div>
</body>
</html>
"""


def render_day_page(day):
    date_str = day["date"]
    picks = day.get("picks", [])
    cards = "\n".join(render_card(p) for p in picks)
    head = page_head(f"{fmt_date(date_str)} · {SITE_TITLE}", "../", "../")
    body = f"""
<main>
  <h1 class="day-title">{esc(fmt_date(date_str))}</h1>
  <p class="day-count">{len(picks)} pick{"s" if len(picks) != 1 else ""}</p>
  <div class="card-grid">
    {cards}
  </div>
</main>
"""
    return head + body + PAGE_FOOT


def render_index(days):
    if days:
        latest = days[0]
        latest_cards = "\n".join(render_card(p) for p in latest.get("picks", []))
        latest_section = f"""
<section>
  <h2 class="section-title">Today &middot; {esc(fmt_date(latest["date"]))}</h2>
  <div class="card-grid">
    {latest_cards}
  </div>
</section>
"""
        older = days[1:]
    else:
        latest_section = (
            '<section><p class="empty-state">No picks yet &mdash; the first daily hunt '
            "hasn't run. See RUNBOOK.md in the repo for how it works.</p></section>"
        )
        older = []

    archive_items = "\n".join(
        f'<li><a href="days/{d["date"]}.html">{esc(fmt_date(d["date"]))}</a> '
        f'<span class="archive-count">{len(d.get("picks", []))} picks</span></li>'
        for d in older
    )
    archive_section = f"""
<section>
  <h2 class="section-title">Archive</h2>
  <ul class="archive-list">
    {archive_items or '<li class="empty-state">Nothing here yet.</li>'}
  </ul>
</section>
"""
    head = page_head(SITE_TITLE, "", "")
    body = f"<main>{latest_section}{archive_section}</main>"
    return head + body + PAGE_FOOT


def main():
    DAYS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    days = load_days()

    for day in days:
        out_path = DAYS_DIR / f"{day['date']}.html"
        out_path.write_text(render_day_page(day))

    INDEX_PATH.write_text(render_index(days))
    print(f"Built {len(days)} day page(s) and index.html")


if __name__ == "__main__":
    main()
