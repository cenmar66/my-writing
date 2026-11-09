#!/usr/bin/env python3
"""Check a draft for every rule a pattern can catch, and every number not backed by sources.md.

  python3 tools/preflight.py issues/2026-11-10-some-slug        # checks draft.md in that folder
  python3 tools/preflight.py path/to/file.md --sources path/to/sources.md

FIX   = breaks a rule in feedback/rules.md. Must be fixed.
CHECK = a number in the text that is not in sources.md. Add the source or cut the number.
NOTE  = [ME: ...] placeholders still waiting for you.
Exit code 1 if any FIX or CHECK.

Adding a rule? If a pattern can catch it, add it to RULES below, same day, with the rule's date.
"""
import argparse
import re
import sys
from pathlib import Path

# Each entry: (rule text as in rules.md, date, regex or callable returning list of matches)
RULES = [
    ("No em dashes.", "2026-11-08", r"—|(?<=\w) -- (?=\w)"),
    ("No semicolons.", "2026-11-08", r";"),
    ("No hashtags in anything I author.", "2026-11-08", r"(?<![\w#&/])#[A-Za-z][\w]*"),
    ("Short sentences and fragments. (flag: sentence over 25 words)", "2026-11-08", "long_sentences"),
]

LONG = 25
NUM_WORDS = (r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|"
             r"sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|"
             r"hundred|thousand|million|billion|half|dozen)")


def strip_for_scan(text):
    """Remove things that are not prose: code, link/image URLs, html comments, heading marks."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"^#{1,6} ", "", text, flags=re.M)
    return text


def strip_front_matter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def long_sentences(text):
    t = re.sub(r"\[ME:[^\]]*\]", "", text)
    t = re.sub(r"[*_>]", "", t)
    out = []
    for s in re.split(r"(?<=[.!?])\s+|\n+", t):
        if len(s.split()) > LONG:
            out.append(s.strip())
    return out


def line_of(text, needle):
    i = text.find(needle)
    return text.count("\n", 0, i) + 1 if i >= 0 else 0


def norm_num(s):
    return s.lower().replace(",", "").replace("$", "").rstrip(".")


def numbers_in(text):
    t = re.sub(r"\[ME:[^\]]*\]", "", text)
    found = re.findall(r"\$?\d[\d,]*(?:\.\d+)?%?", t)
    found += re.findall(r"\b" + NUM_WORDS + r"(?:[- ]" + NUM_WORDS + r")*(?: percent)?\b", t, flags=re.I)
    seen, out = set(), []
    for f in found:
        k = norm_num(f)
        if k and k not in seen:
            seen.add(k)
            out.append(f)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="issue folder or a .md file")
    ap.add_argument("--sources", help="sources.md (default: next to the draft)")
    a = ap.parse_args()
    t = Path(a.target)
    draft = t / "draft.md" if t.is_dir() else t
    sources = Path(a.sources) if a.sources else draft.parent / "sources.md"
    raw = strip_front_matter(draft.read_text(encoding="utf-8"))
    text = strip_for_scan(raw)

    fixes, checks = [], []
    for rule, date, pat in RULES:
        hits = long_sentences(text) if pat == "long_sentences" else [m.group(0) for m in re.finditer(pat, text)]
        for h in hits:
            ctx = h if len(h) > 3 else next((l.strip() for l in text.splitlines() if h in l), h)
            fixes.append(f"FIX   line {line_of(raw, h if len(h) > 3 else ctx)}: {rule} ({date}) -> {ctx[:120]}")

    src = sources.read_text(encoding="utf-8").lower().replace(",", "").replace("$", "") if sources.exists() else ""
    if not sources.exists():
        checks.append(f"CHECK no sources.md at {sources}: every number below is unbacked")
    for n in numbers_in(text):
        k = norm_num(n)
        if not re.search(r"(?<![\w.])" + re.escape(k) + r"(?![\w])", src):
            ctx = next((l.strip() for l in text.splitlines() if n in l), "")
            checks.append(f"CHECK line {line_of(raw, n)}: \"{n}\" is not in sources.md -> {ctx[:100]}")

    notes = [f"NOTE  line {line_of(raw, m)}: {m}" for m in re.findall(r"\[ME:[^\]]*\]", raw)]

    for line in fixes + checks + notes:
        print(line)
    print(f"\npreflight: {len(fixes)} FIX, {len(checks)} CHECK, {len(notes)} [ME] left · {draft}")
    sys.exit(1 if fixes or checks else 0)


if __name__ == "__main__":
    main()
