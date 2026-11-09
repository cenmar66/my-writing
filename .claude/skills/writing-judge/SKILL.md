---
name: writing-judge
description: Checks a draft (issues/<folder>/draft.md) against all of feedback/rules.md and style/, and writes judge.md. Must run in a fresh subagent, never the one that wrote the draft. Never rewrites the draft. Use when writing-draft calls it or the user asks to "judge" or "check" a draft.
---

# writing-judge

You are the checker, not the writer. **Never edit draft.md.** If you wrote this draft in this context, stop and ask for a fresh subagent.

Repo: `~/my-writing`. Input: an issue folder, `issues/<folder>/`.

## Read
- All of `feedback/rules.md`.
- All of `style/`: winners.md, signature.md, format.md, voice.md, retention.md.
- `issues/<folder>/draft.md` and `sources.md`.

## Steps
1. `python3 tools/preflight.py issues/<folder>` and keep its output.
2. **Flow pass.** Read every pair of neighbouring lines. Does each follow from the one before? List each break: line, why it does not follow, the fix.
3. **Rule pass.** Each line that breaks a rule in rules.md or a check in style/retention.md: the line (quoted), the rule (quoted, with its date), the fix (one line).
4. **Facts.** Every fact, number, quote or story not in sources.md and not marked [ME: ...] breaks the First rule. Flag it.
5. **Swap pass.** 3 to 8 places where one of my own words or phrases from `style/signature.md` fits better than the draft's. Quote the draft's words and the swap. Only where it fits naturally, never forced.
6. **Rules that fired.** List every rule from rules.md that fired at least once (exact rule text and date).

## Write `issues/<folder>/judge.md`

```
# Judge · <slug> · <date>

## Preflight
<output>

## Flow
- L<n>: "<line>" does not follow "<previous>". Fix: ...

## Rule breaks
- L<n>: "<line>" · Rule: "<rule>" (date) · Fix: ...

## Swaps
- "<draft words>" → "<my words>" (signature.md: <phrase, count>)

## Rules that fired
- "<rule>" (date)
```

Every 6 months, rules that never appear under "Rules that fired" across all judge.md files are up for deletion, except rules tagged PERMANENT.

Return a 2-line summary: number of breaks, swaps, and the rules that fired.
