---
name: writing-repurpose
description: Use after a piece is published, or when the user asks for the LinkedIn post or Instagram carousel for a piece. Drafts a two-line LinkedIn teaser and an Instagram carousel brief from the published text. Never posts anything.
---

# writing-repurpose

Repo: `~/my-writing`. **Never post anything anywhere.** Drafts only.

## Read
- The published piece in `archive/posts/` (from `Published:` in the issue's notes.md).
- The **First rule** and **Words** section of `feedback/rules.md` (no em dashes, no semicolons, **no hashtags**).
- The 10 newest entries in `feedback/edits-log.md` that mention linkedin or carousel, if any.

## LinkedIn teaser → `issues/<folder>/linkedin.md`
- Exactly **two lines**. Line 1: the hook, ideally a line taken from the piece. Line 2: the turn or the question that makes them click.
- No hashtags. No emojis unless my published piece uses them. Then the link on its own line: the piece's URL.

## Instagram carousel brief → `issues/<folder>/carousel.md`
- One idea per slide. 6 to 10 slides.
- Each slide's text is a **verbatim line from the piece**. Do not rewrite my words. Mark the source paragraph (P3, P7).
- Design: black and white only. Big type, one line per slide, plenty of white space.
- Slide 1: the hook line. Middle slides: the story beats and the lesson. Second to last: the closing question.
- Closing slide, exactly: `Read the full piece on Substack. masteryenterprises.substack.com. Link in bio.`
- Caption: one or two lines, no hashtags.

Run `python3 tools/preflight.py issues/<folder>/linkedin.md --sources issues/<folder>/sources.md` and the same for carousel.md. Fix every FIX.

Commit by path and push: `git add issues/<folder>/linkedin.md issues/<folder>/carousel.md && git commit -m "repurpose: <slug>" && git push`

Show me both in the chat.
