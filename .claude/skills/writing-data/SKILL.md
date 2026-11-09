---
name: writing-data
description: Use when the user shares newsletter stats (Substack views, opens, signups, paid, likes) or asks what works, which pieces did best, or what to write more of. Updates data/posts.csv, style/winners.md and analysis/what-works.md.
---

# writing-data

Repo: `~/my-writing`. About 20 to 30 pieces: numbers are **direction, not statistics**. Use judgment alongside them and say so.

## 1. Refresh
`python3 tools/sync_archive.py` (refreshes likes, comments, restacks on every piece).

## 2. Add what I shared
If I share stats (a screenshot, a CSV, numbers in chat), add them as columns in `data/posts.csv`: `views`, `opens`, `signups`, `paid` (one row per slug). Never add reader-level data (emails, names, per-reader opens). Copy each number into the matching file's front matter in `archive/posts/` too, so tools can read it. Sync keeps these columns.

## 3. Rank
"Best" = the piece's number divided by the median of the 10 pieces published around it. Uses paid, else signups, else likes (`tools/common.py: relative_scores`).
`python3 tools/style_stats.py --write-winners` rebuilds `style/winners.md` with the top 10 openings, word for word.
If the ranking changed a lot, update `style/retention.md` checks to match what the top pieces do.

## 4. What works
Rewrite `analysis/what-works.md`: what my best pieces share that my worst do not (topic cluster, story vs news-led, length, opening type, ending). Each claim names the pieces behind it. Keep the "honest state of the numbers" line current.

## 5. Save
`git add data/posts.csv archive/posts style/winners.md style/retention.md analysis/what-works.md && git commit -m "data: <short>" && git push`
(Only the paths you changed.)

Answer my question in 3 to 5 lines, best and worst by name.
