# my-writing

Private writing repo for the Mastery Enterprises newsletter. Claude drafts, a second Claude checks, and every edit becomes a rule.

## Map

| Folder | What is in it |
|---|---|
| `CLAUDE.md` | Read by Claude in every chat. The short version of how this works. |
| `archive/posts/` | Every published piece, one file each (`YYYY-MM-DD-slug.md`), full text with its numbers at the top. |
| `data/posts.csv` | One row per piece with its numbers (likes, comments, restacks, plus views/opens/signups/paid when shared). |
| `style/` | What the judge compares drafts to, built from the archive only: `winners.md` (how the best pieces open), `signature.md` (my words and the AI tells I never use), `format.md`, `voice.md`, `retention.md` (open, flow, end checks). |
| `analysis/what-works.md` | What the best pieces share that the worst do not. |
| `feedback/rules.md` | My rules. Beats everything. |
| `feedback/edits-log.md` | Every edit I gave, newest first, in my words. |
| `issues/` | One folder per piece (`YYYY-MM-DD-slug/`): `notes.md`, `sources.md`, `draft.md`, `judge.md`, `paste.html`, `published-diff.md`, `linkedin.md`, `carousel.md`, `checker/`. Plus `backlog.md` for ideas. |
| `research/` | Long reports, one dated file each. Read only when needed. |
| `tools/` | Python scripts, standard library only. See `tools/README.md`. |
| `.claude/skills/` | The 7 skills: pitch, draft, judge, edit, publish, repurpose, data. |
| `.claude/hooks/git_guard.py` | Blocks git commands that could erase another chat's work. Registered in `.claude/settings.json`. |

## How I use it

Just talk. "I have an idea about...", "go", "change this line to...", "I published it", "here are my stats".

## On a new computer

```bash
git clone https://github.com/cenmar66/my-writing ~/my-writing
python3 ~/my-writing/tools/install_global.py
```

The second line lets any Claude Code chat use the skills (links them into `~/.claude/skills/`, adds the git guard and one line to `~/.claude/CLAUDE.md`). It never erases what is already there.
