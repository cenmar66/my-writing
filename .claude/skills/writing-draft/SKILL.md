---
name: writing-draft
description: Use after the user says "go" on a piece that was just pitched (issues/<folder>/notes.md exists). Asks 3 questions, writes draft.md, runs the judge, applies its findings, runs preflight, builds the paste page and gives a link.
---

# writing-draft

Repo: `~/my-writing`. The writer drafts free. The judge reads the rules. Keep it that way.

## 1. Ask first
Ask me **3 quick questions** about my opinions and stories for this piece (one line each). For example: what happened, what I believe about it, what I still get wrong. Wait. Add my answers word for word to `notes.md` under "My answers" and any new facts to `sources.md` as "from me (date)".

## 2. Read (and only this)
- `issues/<folder>/notes.md` and `sources.md`
- The **First rule** in `feedback/rules.md`. **Never read the rest of rules.md.** A writer loaded with rules writes to tick boxes.
- 2 or 3 of my closest past pieces (listed in notes.md; else `python3 tools/closest.py "<idea>"`).
- The newest piece in `archive/posts/` for my standard blocks.

## 3. Write `issues/<folder>/draft.md`
- `# Title`, then `*subtitle*`, then the piece.
- Every fact and number must be in `sources.md`. My feelings, memories and opinions I did not give you: write `[ME: what only I can say here]`. Never invent a story, quote or feeling.
- **Standard blocks**: copy how my latest piece closes, word for word in shape (for example "So let me ask you." then a bold question). The question itself is new.
- Length and shape like the 2 or 3 close pieces you read.

## 4. Judge, then fix
Run the **writing-judge** skill in a fresh subagent (Agent tool, general-purpose). Pass it only the issue folder path. When `judge.md` comes back, apply **only** its findings (rule breaks and the swaps it lists). Do not add your own changes.

## 5. Preflight and paste page
- `python3 tools/preflight.py issues/<folder>`: fix every FIX. For every CHECK, add the source to sources.md or cut the number. [ME] notes stay for me.
- `python3 tools/build_paste.py issues/<folder>`

## 6. Give me a link
Publish `paste.html` as a private Artifact (claude-artifacts publish tool, if you have it) and give me the link. If not, give the file path.
Write the link on the `Draft:` line in notes.md.

Commit by path and push: `git add issues/<folder>/draft.md issues/<folder>/judge.md issues/<folder>/notes.md issues/<folder>/sources.md issues/<folder>/paste.html && git commit -m "draft: <slug>" && git push`

Tell me in 2 lines: the link, and how many [ME: ...] are waiting for me.
