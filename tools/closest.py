#!/usr/bin/env python3
"""Find my closest past pieces to an idea, with their numbers. Used by writing-pitch.

  python3 tools/closest.py "idea in a sentence or two" [-k 3]

Shows each piece's similarity, numbers and relative score (number / median of the 10 around it),
and warns if a close piece came out in the last 2 months.
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import all_posts, closest, metric, relative_scores, today


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("idea")
    ap.add_argument("-k", type=int, default=3)
    a = ap.parse_args()
    posts = all_posts()
    rel = {p["slug"]: s for p, s in relative_scores(posts)}
    cutoff = today() - timedelta(days=61)
    for sim, p in closest(a.idea, posts, k=a.k):
        v, f = metric(p)
        s = rel.get(p["slug"])
        score = f"{s:.2f}x the pieces around it" if s is not None else "no score yet (neighbours at 0)"
        recent = " · COVERED IN THE LAST 2 MONTHS" if date.fromisoformat(p["date"]) >= cutoff and sim >= 0.15 else ""
        print(f"{sim:.2f}  {p['date']}  {p['title']}  ·  {f} {v:g} · {score}{recent}")
        print(f"      {p['path'].relative_to(p['path'].parents[2])}")


if __name__ == "__main__":
    main()
