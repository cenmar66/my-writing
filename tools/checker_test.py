#!/usr/bin/env python3
"""Blind test: does feedback/rules.md describe how I write?

After publishing (diff_published.py has written pairs.json):

  python3 tools/checker_test.py prepare issues/2026-11-10-some-slug
      -> writes checker/pairs.md (each rewritten passage as A/B, mine and the draft's, random order)
         and checker/.key.json (which one is mine). The subagent must NOT read the key.

  Then a FRESH subagent reads ONLY feedback/rules.md and checker/pairs.md, and writes
  checker/picks.md with one line per pair: "1: A" (the one that follows the rules better).

  python3 tools/checker_test.py score issues/2026-11-10-some-slug
      -> % of pairs where it picked my version. Adds the score to notes.md.

High score = the rules capture my edits. Low score = my edits teach something rules.md does not say yet.
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import today


def prepare(issue):
    pairs = json.loads((issue / "pairs.json").read_text(encoding="utf-8"))
    pairs = [p for p in pairs if p["draft"].strip() and p["published"].strip()]
    d = issue / "checker"
    d.mkdir(exist_ok=True)
    rng = random.SystemRandom()
    key, out = {}, ["# Blind pairs", "",
                    "For each pair, pick the version that better follows feedback/rules.md.",
                    "Write your answers to checker/picks.md, one line per pair, like `1: A`.", ""]
    for n, p in enumerate(pairs, 1):
        mine_first = rng.random() < 0.5
        a, b = (p["published"], p["draft"]) if mine_first else (p["draft"], p["published"])
        key[str(n)] = "A" if mine_first else "B"
        out += [f"## Pair {n}", "", f"**A:** {a}", "", f"**B:** {b}", ""]
    (d / "pairs.md").write_text("\n".join(out), encoding="utf-8")
    (d / ".key.json").write_text(json.dumps(key), encoding="utf-8")
    print(f"{len(pairs)} blind pairs in {d / 'pairs.md'}" if pairs else "No rewritten passages: nothing to test.")


def score(issue):
    d = issue / "checker"
    key = json.loads((d / ".key.json").read_text(encoding="utf-8"))
    picks = dict(re.findall(r"^\s*(\d+)\s*[:.)-]\s*([ABab])\b", (d / "picks.md").read_text(encoding="utf-8"), re.M))
    graded = [n for n in key if n in picks]
    hits = sum(1 for n in graded if picks[n].upper() == key[n])
    if not graded:
        sys.exit("No picks found in checker/picks.md")
    pct = 100 * hits / len(graded)
    line = f"Checker score: {pct:.0f}% ({hits} of {len(graded)} pairs picked my version) · {today().isoformat()}"
    notes = issue / "notes.md"
    text = notes.read_text(encoding="utf-8") if notes.exists() else ""
    text = re.sub(r"^Checker score:.*$\n?", "", text, flags=re.M)
    notes.write_text(text.rstrip() + "\n\n" + line + "\n", encoding="utf-8")
    print(line)


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("prepare", "score"):
        sys.exit(__doc__)
    {"prepare": prepare, "score": score}[sys.argv[1]](Path(sys.argv[2]))
