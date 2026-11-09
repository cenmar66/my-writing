---
name: writing-edit
description: Use every time the user corrects anything about their writing: a draft, a title, a pitch, a teaser, a carousel, the tone, a word. Logs their exact words, turns lasting corrections into rules (and preflight patterns), applies the edit, and pushes.
---

# writing-edit

Repo: `~/my-writing`. My edits are how this system learns. Every one gets logged.

## 1. Log it, word for word
Add at the **top** of `feedback/edits-log.md` (newest first):

```
## YYYY-MM-DD · <piece-slug or "general">
I said: "<my exact words, copied, never paraphrased>"
What changed: <what you edited>
→ rule: <the rule line> (or → one-off)
```

## 2. Rule or one-off?
If it will apply again (to future pieces, not just this sentence), it is a rule. I said it, so it is mine: **add it yourself**, no need to ask.
- Add one line to the right section of `feedback/rules.md` (Facts, Ideas and titles, Opening, Flow, Words, Format, Ending), ending with the date: `- <rule>. (YYYY-MM-DD)`
- Keep it short. If an existing rule covers it, sharpen that rule instead of adding a near-duplicate.
- **If a pattern can catch it** (a word, a punctuation mark, a phrase, a length), add it to `RULES` in `tools/preflight.py` the same day, with the same rule text and date. Then run `python3 tools/preflight.py issues/<folder>` to confirm it fires where it should.
- Never delete or weaken a rule tagged PERMANENT.

## 3. Apply it
Make the edit. If it was a draft: `python3 tools/build_paste.py issues/<folder>` and republish the paste page Artifact if there is one.

## 4. Save to GitHub
Commit only the files you changed, by path, and push:
`git add feedback/edits-log.md feedback/rules.md tools/preflight.py issues/<folder>/draft.md issues/<folder>/paste.html && git commit -m "edit: <short>" && git push`
(Leave out any path you did not change.)

Reply in one line: what changed and the rule it became (or "one-off").
