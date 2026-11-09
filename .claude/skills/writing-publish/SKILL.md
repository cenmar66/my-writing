---
name: writing-publish
description: Use when the user says they published a piece on Substack. Pulls it into the archive, diffs it against the draft, logs the lessons, proposes rules (adds only after a yes), runs the blind checker test, and sets the results date.
---

# writing-publish

Repo: `~/my-writing`. Find the issue folder (the one being worked on, or ask).

## 1. Pull it in
`python3 tools/sync_archive.py --new`. If it says a piece is cut at the paywall, ask me for a fresh Substack export (Settings → Exports → Create new export, then download it) and run `python3 tools/sync_archive.py --export <path>`. Never copy the export's reader files (email list, opens, delivers) into the repo.
Add `Published: archive/posts/<file>.md` to notes.md.

## 2. Diff
`python3 tools/diff_published.py issues/<folder>` → `published-diff.md` and `pairs.json`.

## 3. Log what I changed, once, grouped by lesson
One entry at the top of `feedback/edits-log.md`:

```
## YYYY-MM-DD · <slug> (published)
I said: (my edits in Substack, see issues/<folder>/published-diff.md)
What changed:
- <lesson 1>: P3, P7 (e.g. "cut the explanation after the story")
- <lesson 2>: P5
→ proposed rules: see below
```
Group edits by lesson, not by paragraph. No bloat: 2 to 6 lessons max.

## 4. Propose rules, add only after my yes
You guessed these from my edits, so I decide. List each lasting lesson as a one-line rule with its section. Ask "Add these? (yes / no / edit each)". Add only the ones I approve to `feedback/rules.md` (with today's date) and to `tools/preflight.py` if a pattern can catch them. Mark the log line `→ rule` or `→ one-off` to match.

## 5. Blind checker test
1. `python3 tools/checker_test.py prepare issues/<folder>`
2. Spawn a **fresh subagent** (Agent tool, general-purpose) with this prompt, nothing else:
   "Read ONLY ~/my-writing/feedback/rules.md and ~/my-writing/issues/<folder>/checker/pairs.md. Do not open any other file. For each pair pick the version that better follows the rules. Write ~/my-writing/issues/<folder>/checker/picks.md with one line per pair like `1: A`."
3. `python3 tools/checker_test.py score issues/<folder>` → tell me the score in one line.

## 6. Results date
Add `Results due: <publish date + 7 days>` to notes.md. (Every chat checks `python3 tools/results.py --due`; when due, run `python3 tools/sync_archive.py` then `python3 tools/results.py issues/<folder>` and tell me the result in 2 lines.)

## 7. Commit the whole issue folder, by path
`git add issues/<folder> archive/posts/<file>.md data/posts.csv feedback/edits-log.md feedback/rules.md tools/preflight.py && git commit -m "published: <slug>" && git push`
(Leave out rules.md and preflight.py if I approved no rules.)

Then offer writing-repurpose.
