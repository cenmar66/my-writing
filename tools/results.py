#!/usr/bin/env python3
"""A week after publishing: how did the piece do against my closest past pieces?

  python3 tools/results.py --due                       # list issues whose "Results due:" date has come
  python3 tools/results.py issues/2026-11-10-some-slug # compare and add the result to notes.md

Run tools/sync_archive.py first so the numbers are fresh.
"Closest" = the 5 past pieces most similar in topic (words), published before this one.
"""
import re
import statistics
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ISSUES, all_posts, body_text, closest, num, today

FIELDS = ["likes", "comments", "restacks", "views", "opens", "signups", "paid"]


def due():
    out = []
    for notes in sorted(ISSUES.glob("*/notes.md")):
        t = notes.read_text(encoding="utf-8")
        m = re.search(r"Results due:\s*(\d{4}-\d{2}-\d{2})", t)
        if m and date.fromisoformat(m.group(1)) <= today() and "## Results" not in t:
            out.append(notes.parent)
    return out


def published_post(issue, posts):
    t = (issue / "notes.md").read_text(encoding="utf-8")
    m = re.search(r"Published:\s*archive/posts/(\S+)\.md", t)
    if m:
        return next((p for p in posts if Path(p["path"]).stem == m.group(1)), None)
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", issue.name)
    return next((p for p in reversed(posts) if p.get("slug") == slug), None)


def run(issue):
    posts = all_posts()
    me = published_post(issue, posts)
    if not me:
        sys.exit("Published piece not in archive/. Run tools/sync_archive.py --new first.")
    past = [p for p in posts if p["date"] < me["date"]]
    near = closest(me.get("title", "") + "\n" + body_text(me["body"]), past, k=5)
    lines = [f"## Results ({today().isoformat()})", "",
             f"Compared with my {len(near)} closest past pieces: " + ", ".join(p["title"] for _, p in near), ""]
    for f in FIELDS:
        mine = num(me.get(f))
        vals = [num(p.get(f)) for _, p in near if num(p.get(f)) is not None]
        if mine is None or not vals:
            continue
        med = statistics.median(vals)
        rel = f"{mine / med:.1f}x their median" if med else "their median is 0"
        lines.append(f"- {f}: {mine:g} vs median {med:g} ({rel})")
    if len(lines) == 4:
        lines.append("- No numbers to compare yet.")
    notes = issue / "notes.md"
    notes.write_text(notes.read_text(encoding="utf-8").rstrip() + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--due":
        d = due()
        print("\n".join(str(x) for x in d) if d else "No results due.")
    elif len(sys.argv) == 2:
        run(Path(sys.argv[1]))
    else:
        sys.exit(__doc__)
