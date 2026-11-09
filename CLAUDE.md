# My writing repo

Mastery Enterprises newsletter (Substack), plus LinkedIn and Instagram from each piece.

- This repo is the only source of truth. Nothing about my writing lives anywhere else.
- `feedback/rules.md` is my word and beats everything, including style/ and these lines.
- The writer drafts free (First rule only). The judge, in a fresh subagent, reads all the rules.
- Log every edit I give in `feedback/edits-log.md`, in my exact words.
- Start of every chat: `python3 tools/results.py --due`. If anything is due, run it (see writing-publish).

Skills:
- writing-pitch: I bring an idea
- writing-draft: I say "go"
- writing-judge: checks a draft (never the writer)
- writing-edit: I correct anything
- writing-publish: I say I published
- writing-repurpose: LinkedIn teaser and carousel brief
- writing-data: I share stats or ask what works

Git: commit only the files you changed, by path (`git add path/a path/b`), then push. Never `git add -A` or `.`, never force. `.claude/hooks/git_guard.py` blocks the rest.

Tools: `tools/README.md`. Map: `README.md`.
