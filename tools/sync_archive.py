#!/usr/bin/env python3
"""Pull published Substack pieces into archive/posts/ and data/posts.csv.

  python3 tools/sync_archive.py            # all pieces: add new ones, refresh numbers on old ones
  python3 tools/sync_archive.py --new      # only add pieces not in the archive yet
  python3 tools/sync_archive.py --export ~/Downloads/export.zip
        # fill in paid pieces' full text from a Substack export (zip or unzipped folder).
        # Reads ONLY posts.csv and posts/<id>.<slug>.html. Never copies reader files
        # (email list, opens, delivers, subscribers) anywhere.

Public API, no login: /api/v1/archive (list) and /api/v1/posts/<slug> (one piece).
The API cuts paid pieces at the paywall; those get `paywalled: true` and a cut marker.
"""
import argparse
import re
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (ARCHIVE, DATA_CSV, PAYWALL_MARK, PUB, all_posts, fetch_json, html_to_md,
                    read_csv, read_post, today, write_csv, write_post)

BASE_FIELDS = ["date", "slug", "title", "likes", "comments", "restacks", "wordcount",
               "audience", "paywalled", "url"]


def list_archive():
    posts, cursor = [], None
    while True:
        url = f"{PUB}/api/v1/archive?sort=new"
        if cursor:
            url += "&cursor=" + urllib.parse.quote(cursor)
        d = fetch_json(url)
        batch = d.get("posts", []) if isinstance(d, dict) else d
        posts += batch
        cursor = d.get("nextCursor") if isinstance(d, dict) else None
        if not batch or not cursor:
            return posts
        time.sleep(0.5)


def path_for(p):
    return ARCHIVE / f"{p['post_date'][:10]}-{p['slug']}.md"


def existing_by_slug():
    out = {}
    for f in ARCHIVE.glob("*.md"):
        meta, _ = read_post(f)
        out[meta.get("slug", "")] = f
    return out


def save_post(full, old_path=None):
    body_md = html_to_md(full.get("body_html") or "")
    words = len(body_md.split())
    paywalled = full.get("audience") in ("only_paid", "founding") or (
        (full.get("wordcount") or 0) > 0 and words < 0.7 * full["wordcount"])
    keep_old_body = False
    old_meta = {}
    if old_path and old_path.exists():
        old_meta, old_body = read_post(old_path)
        # keep text filled in from an export: the API only has the part before the paywall
        if old_meta.get("filled_from_export") == "true":
            keep_old_body = True
    meta = {
        "title": (full.get("title") or "").replace("\n", " "),
        "subtitle": (full.get("subtitle") or "").replace("\n", " "),
        "date": full["post_date"][:10],
        "slug": full["slug"],
        "url": full.get("canonical_url") or f"{PUB}/p/{full['slug']}",
        "likes": full.get("reaction_count") or 0,
        "comments": full.get("comment_count") or 0,
        "restacks": full.get("restacks") or 0,
        "wordcount": full.get("wordcount") or 0,
        "audience": full.get("audience") or "",
        "paywalled": "true" if paywalled else "false",
        "synced": today().isoformat(),
    }
    for k, v in old_meta.items():  # keep numbers added by hand (views, opens, signups, paid)
        meta.setdefault(k, v)
    if keep_old_body:
        meta["filled_from_export"] = "true"
        body = old_body
    else:
        head = f"# {meta['title']}\n\n" + (f"*{meta['subtitle']}*\n\n" if meta["subtitle"] else "")
        body = head + body_md + (f"\n\n{PAYWALL_MARK}\n" if paywalled else "")
    target = path_for(full)
    if old_path and old_path == target and old_path.exists():
        same = {k: v for k, v in old_meta.items() if k != "synced"} == {k: str(v) for k, v in meta.items() if k != "synced"}
        if same and read_post(old_path)[1].strip() == body.strip():
            return target, old_meta  # nothing changed: leave the file alone

    if old_path and old_path != target and old_path.exists():
        old_path.unlink()
    write_post(target, meta, body)
    return target, meta


def rebuild_csv():
    rows, fields = read_csv()
    by_slug = {r.get("slug"): r for r in rows}
    fields = BASE_FIELDS + [f for f in fields if f not in BASE_FIELDS]  # keep columns added by hand (signups, paid...)
    out = []
    for p in all_posts():
        row = dict(by_slug.get(p["slug"], {}))
        row.update({k: p.get(k, "") for k in BASE_FIELDS})
        out.append(row)
    write_csv(out, fields)


def fill_from_export(src):
    src = Path(src).expanduser()
    if src.is_dir():
        names = {str(p.relative_to(src)).replace("\\", "/"): p for p in src.rglob("*")}
        read = lambda n: names[n].read_text(encoding="utf-8", errors="replace")
    else:
        z = zipfile.ZipFile(src)
        names = {n: n for n in z.namelist()}
        read = lambda n: z.read(n).decode("utf-8", errors="replace")
    post_html = {}
    for n in names:
        m = re.search(r"(?:^|/)posts/(\d+)\.([^/]+?)\.html$", n)  # only the piece files
        if m:
            post_html[m.group(2)] = n
    by_slug = existing_by_slug()
    filled = 0
    for slug, path in by_slug.items():
        meta, body = read_post(path)
        if meta.get("paywalled") != "true" or slug not in post_html:
            continue
        md = html_to_md(read(post_html[slug]))
        head = f"# {meta['title']}\n\n" + (f"*{meta['subtitle']}*\n\n" if meta.get("subtitle") else "")
        meta["filled_from_export"] = "true"
        write_post(path, meta, head + md)
        filled += 1
    still = [s for s, p in by_slug.items()
             if read_post(p)[0].get("paywalled") == "true" and read_post(p)[0].get("filled_from_export") != "true"]
    print(f"Filled {filled} paid piece(s) from the export. Still cut at the paywall: {len(still)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", action="store_true", help="only add pieces not archived yet")
    ap.add_argument("--export", help="Substack export zip or folder, to fill paid pieces")
    a = ap.parse_args()
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    if a.export:
        fill_from_export(a.export)
        rebuild_csv()
        return
    have = existing_by_slug()
    listing = [p for p in list_archive() if p.get("type") in ("newsletter", "thread", "podcast", None)]
    added, refreshed, cut = [], 0, []
    for p in listing:
        old = have.get(p["slug"])
        if a.new and old:
            continue
        full = fetch_json(f"{PUB}/api/v1/posts/{p['slug']}")
        target, meta = save_post(full, old)
        if old:
            refreshed += 1
        else:
            added.append(target.name)
        if meta["paywalled"] == "true" and meta.get("filled_from_export") != "true":
            cut.append(target.name)
        time.sleep(0.5)
    rebuild_csv()
    print(f"Added {len(added)}, refreshed numbers on {refreshed}. Archive now has {len(list(ARCHIVE.glob('*.md')))} pieces.")
    for n in added:
        print("  +", n)
    if cut:
        print(f"{len(cut)} paid piece(s) are cut at the paywall. Fill them with a Substack export:")
        print("  Substack > Settings > Exports > Create new export, download it, then:")
        print("  python3 tools/sync_archive.py --export <path to the zip>")


if __name__ == "__main__":
    main()
