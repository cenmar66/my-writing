#!/usr/bin/env python3
"""Compare my draft with what was published, paragraph by paragraph.

  python3 tools/diff_published.py issues/2026-11-10-some-slug [--published archive/posts/FILE.md]

Finds the published piece by the slug in the folder name (or `Published: archive/posts/...` in notes.md).
Each paragraph is matched at most once (best matches first). Nothing past a paywall cut is compared.
Writes published-diff.md and pairs.json (rewritten passages, used by checker_test.py).
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ARCHIVE, PAYWALL_MARK, body_text, paragraphs, read_post

MATCH = 0.45   # below this, two paragraphs are not the same passage
SAME = 0.97    # at or above, counted as unchanged


def find_published(issue):
    notes = issue / "notes.md"
    if notes.exists():
        m = re.search(r"Published:\s*(archive/posts/\S+\.md)", notes.read_text(encoding="utf-8"))
        if m:
            return issue.parent.parent / m.group(1)
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", issue.name)
    hits = sorted(ARCHIVE.glob(f"*-{slug}.md"))
    return hits[-1] if hits else None


def clean(p):
    p = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", p)
    return re.sub(r"\s+", " ", p.replace("**", "").replace("*", "")).strip()


def ratio(a, b):
    return difflib.SequenceMatcher(None, clean(a).lower(), clean(b).lower()).ratio()


def word_diff(a, b):
    aw, bw = clean(a).split(), clean(b).split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, aw, bw).get_opcodes():
        if op == "equal":
            out.append(" ".join(aw[i1:i2]))
        if op in ("delete", "replace"):
            out.append("~~" + " ".join(aw[i1:i2]) + "~~")
        if op in ("insert", "replace"):
            out.append("**" + " ".join(bw[j1:j2]) + "**")
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("issue")
    ap.add_argument("--published")
    a = ap.parse_args()
    issue = Path(a.issue)
    pub_path = Path(a.published) if a.published else find_published(issue)
    if not pub_path or not pub_path.exists():
        sys.exit("No published piece found. Run tools/sync_archive.py --new, or pass --published.")
    pmeta, pbody = read_post(pub_path)
    cut = PAYWALL_MARK in pbody and pmeta.get("filled_from_export") != "true"
    pub = paragraphs(body_text(pbody))
    _, dbody = read_post(issue / "draft.md")
    draft = paragraphs(body_text(dbody))
    if cut:  # only compare draft paragraphs up to the length the public text reaches
        draft = draft[:len(pub) + 2]

    cands = sorted(((ratio(d, p), i, j) for i, d in enumerate(draft) for j, p in enumerate(pub)), reverse=True)
    used_d, used_p, pairs = set(), set(), []
    for r, i, j in cands:
        if r < MATCH:
            break
        if i in used_d or j in used_p:
            continue
        used_d.add(i)
        used_p.add(j)
        pairs.append((i, j, r))
    pairs.sort(key=lambda x: x[1])
    same = [x for x in pairs if x[2] >= SAME]
    rewritten = [x for x in pairs if x[2] < SAME]
    cut_d = [i for i in range(len(draft)) if i not in used_d]
    added = [j for j in range(len(pub)) if j not in used_p]
    kept = 100 * len(same) / max(len(draft), 1)

    out = [f"# Published diff: {pmeta.get('title', issue.name)}", "",
           f"Draft: {issue / 'draft.md'} · Published: {pub_path.name}" + (" · compared up to the paywall cut" if cut else ""),
           "", f"Paragraphs: {len(draft)} in draft, {len(pub)} published. "
           f"Unchanged {len(same)} ({kept:.0f}%), rewritten {len(rewritten)}, cut {len(cut_d)}, added {len(added)}.", ""]
    out += ["## Rewritten (~~mine~~ → **yours**)", ""]
    for i, j, r in rewritten:
        out += [f"**P{j+1}** (similarity {r:.2f})", "", "Draft: " + draft[i], "", "Published: " + pub[j], "",
                "Diff: " + word_diff(draft[i], pub[j]), ""]
    out += ["## Cut from the draft", ""] + [f"- {draft[i]}" for i in cut_d] + [""]
    out += ["## Added by you", ""] + [f"- P{j+1}: {pub[j]}" for j in added] + [""]
    out += ["## Unchanged", ""] + [f"- P{j+1}: {pub[j][:80]}" for i, j, r in same] + [""]
    (issue / "published-diff.md").write_text("\n".join(out), encoding="utf-8")
    pj = [{"draft": draft[i], "published": pub[j]} for i, j, r in rewritten]
    (issue / "pairs.json").write_text(json.dumps(pj, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"published-diff.md written: {len(same)} unchanged, {len(rewritten)} rewritten, {len(cut_d)} cut, {len(added)} added.")


if __name__ == "__main__":
    main()
