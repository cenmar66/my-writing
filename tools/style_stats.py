#!/usr/bin/env python3
"""Counts from the archive that style/ is built on. Prints a report; changes nothing.

  python3 tools/style_stats.py
  python3 tools/style_stats.py --write-winners   # rebuild style/winners.md from the numbers

Used to (re)build style/signature.md and style/format.md when the archive grows.
"""
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, STOP, all_posts, body_text, metric, paragraphs, relative_scores

# Words and moves that machine-written text leans on. Counted in the archive to prove absence.
AI_TELLS = [
    "—", ";", "delve", "tapestry", "testament", "navigate", "navigating", "landscape", "realm",
    "crucial", "pivotal", "foster", "leverage", "robust", "seamless", "unlock", "elevate", "embark",
    "game-changer", "dive into", "deep dive", "moreover", "furthermore", "additionally",
    "in conclusion", "ultimately", "vibrant", "intricate", "multifaceted", "harness", "resonate",
    "transformative", "empower", "holistic", "nuanced", "beacon", "underscore", "showcase",
    "paramount", "meticulous", "ever-evolving", "fast-paced", "here's the thing", "the truth is",
    "picture this", "imagine a", "whether you're", "at the end of the day", "it's not just",
    "not only", "let's", "unpack", "journey", "#",
]


def sentences(text):
    text = re.sub(r"[*_#>]", "", text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in parts if re.search(r"[A-Za-z0-9]", s)]


def count(phrase, text):
    if phrase in ("—", ";", "#"):
        if phrase == "#":
            return len(re.findall(r"(?<![\w#])#[A-Za-z]\w*", text))
        return text.count(phrase)
    return len(re.findall(r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])", text.lower()))


def main():
    posts = all_posts()
    texts = [body_text(p["body"]) for p in posts]
    alltext = "\n\n".join(texts)
    n = len(posts)
    print(f"# Archive stats ({n} pieces, {posts[0]['date']} to {posts[-1]['date']})\n")

    wc = [len(re.findall(r"\b\w+\b", t)) for t in texts]
    print(f"Words per piece: median {statistics.median(wc):.0f}, min {min(wc)}, max {max(wc)}")
    sl = [len(s.split()) for t in texts for s in sentences(t)]
    print(f"Words per sentence: median {statistics.median(sl):.0f}, mean {statistics.mean(sl):.1f}, "
          f"90th pct {sorted(sl)[int(len(sl)*.9)]}, max {max(sl)}")
    print(f"Sentences of 1-4 words (fragments): {sum(1 for x in sl if x <= 4)} of {len(sl)} "
          f"({100*sum(1 for x in sl if x <= 4)/len(sl):.0f}%)")
    print(f"Sentences over 25 words: {sum(1 for x in sl if x > 25)}")
    pl = [len(sentences(p)) for t in texts for p in paragraphs(t)]
    print(f"Sentences per paragraph: median {statistics.median(pl):.0f}, max {max(pl)}")
    heads = [sum(1 for l in t.splitlines() if l.startswith("#") or re.match(r"^\*\*[^*]+\*\*$", l.strip()) and not l.strip().endswith("?**")) for t in texts]
    print(f"Pieces with section headings: {sum(1 for h in heads if h)} of {n}")
    lists = sum(1 for t in texts if re.search(r"^(- |\d+\. )", t, re.M))
    print(f"Pieces with bullet/numbered lists: {lists} of {n}")

    print("\n## Endings")
    last = [paragraphs(t)[-1] for t in texts]
    print(f"Ends on a question: {sum(1 for l in last if l.rstrip('*').rstrip().endswith('?'))} of {n}")
    print(f"Ending question in bold: {sum(1 for l in last if l.strip().endswith('?**'))} of {n}")
    print(f"'So let me ask you' anywhere: {count('so let me ask you', alltext)}")
    print(f"'Takeaway:' line: {count('takeaway:', alltext.replace('**', ''))}")

    print("\n## Signature phrases (count, pieces)")
    phrases = ["not performance. presence.", "that is the trade", "so let me ask you", "that is the whole game",
               "the whole game", "fellow traveler", "i am not a guru", "permission", "armor", "presence",
               "attention", "the practice", "payroll", "boardroom", "chair", "return", "sanding",
               "earth school", "zen mind = beginner's mind", "here is", "i watched", "not because",
               "you do not need", "that is the", "real work", "honest"]
    for ph in phrases:
        c = count(ph, alltext.replace("**", ""))
        pieces = sum(1 for t in texts if count(ph, t.replace("**", "")))
        print(f"  {ph!r}: {c} ({pieces} pieces)")

    print("\n## Contractions vs spelled out")
    contr = re.findall(r"\b\w+'(?:t|s|re|ve|ll|d|m)\b", alltext.replace("’", "'").lower())
    contr = [c for c in contr if not re.match(r"^\w+'s$", c) or c in ("it's", "that's", "here's", "there's", "what's", "let's")]
    spelled = re.findall(r"\b(?:do not|does not|did not|is not|are not|was not|can not|cannot|will not|i am|it is|that is|i have|you are)\b", alltext.lower())
    print(f"  contractions: {len(contr)} {Counter(contr).most_common(8)}")
    print(f"  spelled out: {len(spelled)} {Counter(spelled).most_common(8)}")

    print("\n## Pronouns per 1000 words")
    words = re.findall(r"[a-z']+", alltext.lower())
    for w in ["i", "my", "me", "you", "your", "we", "our"]:
        print(f"  {w}: {1000*words.count(w)/len(words):.1f}")

    print("\n## Most used content words")
    cw = Counter(w for w in words if w not in STOP and len(w) > 3)
    print("  " + ", ".join(f"{w} {c}" for w, c in cw.most_common(40)))

    print("\n## 'Not X. Y.' pivots")
    piv = re.findall(r"(?:^|\n|\. )(Not [^.?!\n]{1,40}\.\s+[A-Z][^.?!\n]{1,40}\.)", alltext.replace("**", ""))
    for x in piv:
        print("  ", x.strip())

    print("\n## AI tells in the archive (count)")
    for t in AI_TELLS:
        c = count(t, alltext)
        print(f"  {t!r}: {c}")


def write_winners():
    posts = all_posts()
    scored = relative_scores(posts)
    ranked = sorted([x for x in scored if x[1] is not None], key=lambda x: -x[1])[:10]
    out = ["# How my best pieces open", "",
           "Built by `tools/style_stats.py --write-winners` from archive/ only. Word for word.",
           "\"Best\" = the piece's number (paid, else signups, else likes) divided by the median of the 10 pieces published around it.", ""]
    if ranked:
        out.append(f"Top {len(ranked)} of {len(posts)} pieces.")
        items = ranked
    else:
        out += ["**Not ranked yet.** Every piece has 0 likes, 0 comments and 0 restacks on the public API, so there is",
                "no \"best\" to compute. Until numbers come in (likes, or views/opens/signups from the Substack dashboard",
                "via writing-data), this file holds every opening, newest first, so the judge sees how you open.", ""]
        items = [(p, None) for p in reversed(posts)]
    for p, sc in items:
        v, f = metric(p)
        paras = paragraphs(body_text(p["body"]))
        sub = p.get("subtitle", "")
        out += ["---", "", f"## {p['title']} ({p['date']})" + (f" · score {sc:.2f} ({f} {v:g})" if sc is not None else ""), ""]
        if sub:
            out += [f"Subtitle: *{sub}*", ""]
        out += [q for para in paras[:3] for q in (para, "")]
    (ROOT / "style" / "winners.md").write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print("wrote style/winners.md")


if __name__ == "__main__":
    if "--write-winners" in sys.argv:
        write_winners()
    else:
        main()
