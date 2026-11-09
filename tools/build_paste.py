#!/usr/bin/env python3
"""Turn draft.md into one page (paste.html) with a Copy button that pastes cleanly into Substack.

  python3 tools/build_paste.py issues/2026-11-10-some-slug

Open paste.html, click Copy, click into the Substack editor, paste. Headings, bold, italics, links,
lists, quotes and images come through. Local images (images/ in the issue folder) are embedded.
[ME: ...] placeholders are highlighted in yellow so you cannot miss them.
"""
import base64
import mimetypes
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import esc, read_post


def inline(s, base):
    s = esc(s)
    def img(m):
        alt, src = m.group(1), m.group(2)
        p = (base / src) if not re.match(r"https?://", src) else None
        if p and p.exists():
            mime = mimetypes.guess_type(p.name)[0] or "image/png"
            src = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
        return f'<img src="{src}" alt="{alt}" style="max-width:100%">'
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", img, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
    s = re.sub(r"\[ME:([^\]]*)\]", r'<mark>[ME:\1]</mark>', s)
    s = re.sub(r" {2,}\n|\\\n", "<br>", s)
    return s.replace("\n", "<br>")


def md_to_html(md, base):
    blocks = [b for b in re.split(r"\n\s*\n", md.strip()) if b.strip()]
    out = []
    for b in blocks:
        lines = b.splitlines()
        if re.match(r"^#{1,6} ", b):
            n = len(b.split(" ", 1)[0])
            out.append(f"<h{n}>{inline(b.split(' ', 1)[1].strip(), base)}</h{n}>")
        elif all(re.match(r"^\s*[-*] ", l) for l in lines):
            out.append("<ul>" + "".join(f"<li>{inline(re.sub(r'^\s*[-*] ', '', l), base)}</li>" for l in lines) + "</ul>")
        elif all(re.match(r"^\s*\d+[.)] ", l) for l in lines):
            out.append("<ol>" + "".join(f"<li>{inline(re.sub(r'^\s*\d+[.)] ', '', l), base)}</li>" for l in lines) + "</ol>")
        elif all(l.startswith(">") for l in lines):
            out.append("<blockquote><p>" + inline("\n".join(l.lstrip("> ") for l in lines), base) + "</p></blockquote>")
        elif b.strip() in ("---", "***"):
            out.append("<hr>")
        elif re.fullmatch(r"!\[[^\]]*\]\([^)]+\)", b.strip()):
            out.append(f"<figure>{inline(b.strip(), base)}</figure>")
        else:
            out.append(f"<p>{inline(b, base)}</p>")
    return "\n".join(out)


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · paste</title>
<style>
body{{font:18px/1.6 Georgia,serif;max-width:680px;margin:0 auto;padding:24px;color:#111;background:#fff}}
.bar{{position:sticky;top:0;background:#fff;padding:12px 0;border-bottom:1px solid #ddd;display:flex;gap:12px;align-items:center;font:15px system-ui,sans-serif}}
button{{font:600 15px system-ui,sans-serif;padding:10px 18px;border:0;border-radius:6px;background:#111;color:#fff;cursor:pointer}}
#status{{color:#555}} mark{{background:#ffe866}} .warn{{color:#a00;font:14px system-ui,sans-serif}}
</style></head><body>
<div class="bar"><button id="copy">Copy</button><span id="status">Then click into the Substack editor and paste.</span></div>
{warn}
<div id="piece">
{body}
</div>
<script>
document.getElementById('copy').onclick = async () => {{
  const el = document.getElementById('piece'), s = document.getElementById('status');
  try {{
    await navigator.clipboard.write([new ClipboardItem({{
      'text/html': new Blob([el.innerHTML], {{type: 'text/html'}}),
      'text/plain': new Blob([el.innerText], {{type: 'text/plain'}})
    }})]);
    s.textContent = 'Copied. Paste into Substack.';
  }} catch (e) {{
    const r = document.createRange(); r.selectNodeContents(el);
    const sel = getSelection(); sel.removeAllRanges(); sel.addRange(r);
    document.execCommand('copy'); sel.removeAllRanges();
    s.textContent = 'Copied. Paste into Substack.';
  }}
}};
</script></body></html>
"""


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    issue = Path(sys.argv[1])
    _, body = read_post(issue / "draft.md")
    m = re.match(r"#\s+(.+)", body.strip())
    title = m.group(1).strip() if m else issue.name
    me = len(re.findall(r"\[ME:", body))
    warn = f'<p class="warn">{me} [ME: ...] placeholder(s) still in the text, highlighted below.</p>' if me else ""
    html = PAGE.format(title=esc(title), body=md_to_html(body, issue), warn=warn)
    (issue / "paste.html").write_text(html, encoding="utf-8")
    print(f"paste.html written ({me} [ME] left): {issue / 'paste.html'}")


if __name__ == "__main__":
    main()
