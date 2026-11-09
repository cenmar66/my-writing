---
name: writing-pitch
description: Use when the user brings an idea for a newsletter piece (Mastery Enterprises on Substack) or asks "should I write about X". Scores the idea against their past pieces, outlines it, proposes 4 titles, and saves notes.md and sources.md in a new issue folder. Waits for "go".
---

# writing-pitch

Repo: `~/my-writing` (run every command from there). Read `CLAUDE.md` first if you have not this chat.

## Read (and only this)
1. `feedback/rules.md`: the **First rule** and the sections **Facts** and **Ideas and titles**.
2. `feedback/edits-log.md`: the 10 newest entries.
3. `analysis/what-works.md`.
4. My 3 closest past pieces: `python3 tools/closest.py "<the idea in one or two sentences>"`, then read those 3 files in full.

## Check before outlining. Stop me if:
- The closest pieces did worse than usual (score under 1.0 = below the pieces around them), or
- `closest.py` prints `COVERED IN THE LAST 2 MONTHS` for a piece on the same angle.
Say it in one or two lines with the piece's title and date, and ask whether to change the angle or drop it. If there are no numbers yet, say so in one line and go on.
Also check `issues/backlog.md` and open `issues/*/notes.md` for the same idea.

## Pitch (keep it short)
1. **What is new**: one or two lines. What this piece says that my archive has not said.
2. **Outline**: 4 to 7 lines, one per beat: opening scene/claim, turn, story, lesson, admission, closing question. Follow `style/retention.md`.
3. **Ask me for my biggest true number** for this piece (money, years, people, a stat I read). Do not invent one. Wait for my answer before titles.
4. **4 titles**, each checked against my past titles in `archive/posts/` (no repeats, no near-copies; say which past title each is closest to). 3 to 8 words, title case, like my archive. Add a subtitle for the one you recommend.
5. **Paywall**: if the piece will be paid, say after which beat to cut. Otherwise skip.

## Save
Create `issues/YYYY-MM-DD-slug/` (today's date, slug from the working title):
- `notes.md`: Idea · What is new · Closest past pieces (with scores) · Outline · My answers (my exact words) · Titles · Draft: (link, filled later)
- `sources.md`: every fact or number so far, one line each, with its link or "from me (YYYY-MM-DD)".
Never write a fact without a source you opened or my words.

Commit only those two files by path and push:
`git add issues/<folder>/notes.md issues/<folder>/sources.md && git commit -m "pitch: <slug>" && git push`

Then **wait for my "go"**. Do not draft.
