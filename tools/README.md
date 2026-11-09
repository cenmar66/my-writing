# Tools

Python 3, standard library only. Run from the repo root. You never need to type these: the skills run them.

| Tool | What it does |
|---|---|
| `sync_archive.py` | Pulls published pieces from Substack's public API into `archive/posts/` and `data/posts.csv`. `--new` adds only new ones. `--export <zip>` fills paid pieces' full text from a Substack export (reads only `posts.csv` and `posts/*.html`, never reader files). Keeps numbers you added by hand. |
| `preflight.py` | Checks `draft.md` for every rule a pattern can catch (FIX), flags every number not in `sources.md` (CHECK), and lists `[ME: ...]` left (NOTE). New pattern rules go into its `RULES` list the day the rule is added. |
| `diff_published.py` | My draft vs what was published, paragraph by paragraph (each paragraph matched once, nothing past a paywall cut). Writes `published-diff.md` and `pairs.json`. |
| `build_paste.py` | `draft.md` → `paste.html`: one page with a Copy button that pastes cleanly into the Substack editor, images included. |
| `checker_test.py` | `prepare`: each rewritten passage as a blind A/B pair (mine and the draft's). A fresh subagent that reads only `rules.md` and the pairs picks the one that follows the rules. `score`: how often it picked mine, written to `notes.md`. |
| `results.py` | A week after publishing: the piece's numbers vs my 5 closest past pieces, added to `notes.md`. `--due` lists issues whose results date has come. |
| `closest.py` | My closest past pieces to an idea, with numbers and a "covered in the last 2 months" warning. Used by writing-pitch. |
| `style_stats.py` | Counts behind `style/` (sentence length, signature phrases, AI tells). `--write-winners` rebuilds `style/winners.md` from the numbers. |
| `install_global.py` | Links the 7 skills into `~/.claude/skills/`, registers the git guard in `~/.claude/settings.json`, adds one line to `~/.claude/CLAUDE.md`. Never erases anything. |
| `common.py` | Shared helpers (paths, front matter, scoring, similarity, HTML to markdown). |
