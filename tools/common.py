"""Shared helpers for the writing tools. Standard library only."""
import csv
import datetime as dt
import html
import json
import math
import re
import statistics
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "archive" / "posts"
DATA_CSV = ROOT / "data" / "posts.csv"
ISSUES = ROOT / "issues"
RULES = ROOT / "feedback" / "rules.md"
PUB = "https://masteryenterprises.substack.com"
UA = "my-writing-sync/1.0"
PAYWALL_MARK = "<!-- PAYWALL CUT: the public API stops here -->"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


# ---------- front matter ----------

def read_post(path):
    """Return (meta dict, body str) for a markdown file with simple front matter."""
    text = Path(path).read_text(encoding="utf-8")
    meta = {}
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            for line in text[4:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()
            body = text[end + 5:]
    return meta, body


def write_post(path, meta, body):
    lines = ["---"] + [f"{k}: {v}" for k, v in meta.items()] + ["---", ""]
    Path(path).write_text("\n".join(lines) + body.strip() + "\n", encoding="utf-8")


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def all_posts():
    """All archived posts, oldest first, as dicts (meta + 'body' + 'path')."""
    out = []
    for p in sorted(ARCHIVE.glob("*.md")):
        meta, body = read_post(p)
        meta["body"] = body
        meta["path"] = p
        out.append(meta)
    out.sort(key=lambda m: m.get("date", ""))
    return out


def body_text(body):
    """Article text only: drops the title/subtitle lines and anything past a paywall cut."""
    body = body.split(PAYWALL_MARK)[0]
    lines = [l for l in body.splitlines() if not l.startswith("# ")]
    text = "\n".join(lines).strip()
    first, _, rest = text.partition("\n\n")
    if re.fullmatch(r"\*[^*\n].*[^*\n]\*", first.strip()):  # subtitle line written by sync
        text = rest.strip()
    return text


def paragraphs(text):
    text = text.split(PAYWALL_MARK)[0]
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


# ---------- scoring ----------

def metric(post, field="likes"):
    """The engagement number used for 'best'. Uses signups or paid when present."""
    for f in ([field] if field != "likes" else ["paid", "signups", "likes"]):
        v = num(post.get(f))
        if v is not None and (f == "likes" or v > 0):
            return v, f
    return 0.0, "likes"


def relative_scores(posts, field="likes", window=10):
    """score = metric / median of the `window` pieces published around it.
    Returns list of (post, score or None). None means the neighbours' median is 0,
    so there is nothing to compare against yet."""
    res = []
    vals = [metric(p, field)[0] for p in posts]
    for i, p in enumerate(posts):
        lo = max(0, i - window // 2)
        hi = min(len(posts), lo + window + 1)
        lo = max(0, hi - window - 1)
        neigh = [vals[j] for j in range(lo, hi) if j != i]
        med = statistics.median(neigh) if neigh else 0
        res.append((p, (vals[i] / med) if med else None))
    return res


# ---------- similarity ----------

STOP = set("""a an the and or but if of to in on at for with from by as is are was were be been being it its
this that these those i me my we our you your he she they them their his her not no do does did have has had
so just than then there here what when where who why how all any can could will would should into out up down
over about more most very one two also only own same too s t don am""".split())


def tokens(text):
    return [w for w in re.findall(r"[a-z']+", text.lower()) if w not in STOP and len(w) > 2]


def tfidf_vectors(docs):
    df = {}
    toks = [tokens(d) for d in docs]
    for t in toks:
        for w in set(t):
            df[w] = df.get(w, 0) + 1
    n = len(docs)
    vecs = []
    for t in toks:
        tf = {}
        for w in t:
            tf[w] = tf.get(w, 0) + 1
        vecs.append({w: c * math.log((n + 1) / (df[w] + 0.5)) for w, c in tf.items()})
    return vecs


def cosine(a, b):
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def closest(text, posts, k=3, exclude_slug=None):
    pool = [p for p in posts if p.get("slug") != exclude_slug]
    vecs = tfidf_vectors([text] + [p.get("title", "") + "\n" + body_text(p["body"]) for p in pool])
    scored = sorted(((cosine(vecs[0], v), p) for v, p in zip(vecs[1:], pool)), key=lambda x: -x[0])
    return scored[:k]


# ---------- html -> markdown ----------

class _MD(HTMLParser):
    BLOCK = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.buf = []
        self.list_stack = []
        self.href = []
        self.skip = 0
        self.prefix = ""

    def flush(self):
        text = "".join(self.buf).strip()
        self.buf = []
        if text:
            self.out.append(self.prefix + text)
        self.prefix = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "") or ""
        if self.skip or "subscription-widget" in cls or "button-wrapper" in cls or tag in ("script", "style", "svg", "button"):
            self.skip += 1 if tag in ("div", "script", "style", "svg", "button", "form") else 0
            return
        if tag in self.BLOCK:
            self.flush()
            if tag.startswith("h") and len(tag) == 2:
                self.prefix = "#" * min(int(tag[1]) + 1, 6) + " "
            elif tag == "blockquote":
                self.prefix = "> "
            elif tag == "li":
                kind = self.list_stack[-1] if self.list_stack else "ul"
                self.prefix = ("1. " if kind == "ol" else "- ")
        elif tag in ("ul", "ol"):
            self.flush()
            self.list_stack.append(tag)
        elif tag == "br":
            self.buf.append("  \n")
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "a":
            self.href.append(a.get("href", ""))
            self.buf.append("[")
        elif tag == "img":
            src = a.get("src", "")
            if src:
                self.flush()
                self.out.append(f"![{a.get('alt') or ''}]({src})")
        elif tag == "hr":
            self.flush()
            self.out.append("---")

    def handle_endtag(self, tag):
        if self.skip:
            if tag in ("div", "script", "style", "svg", "button", "form"):
                self.skip -= 1
            return
        if tag in self.BLOCK:
            self.flush()
        elif tag in ("ul", "ol"):
            self.flush()
            if self.list_stack:
                self.list_stack.pop()
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "a":
            href = self.href.pop() if self.href else ""
            self.buf.append(f"]({href})")

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def html_to_md(src):
    p = _MD()
    p.feed(src or "")
    p.flush()
    md = "\n\n".join(x for x in p.out if x.strip() not in ("", "**", "*"))
    md = md.replace("****", "").replace("[]()", "")
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def today():
    return dt.date.today()


def read_csv(path=DATA_CSV):
    if not Path(path).exists():
        return [], []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r), r.fieldnames or []


def write_csv(rows, fields, path=DATA_CSV):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def esc(s):
    return html.escape(s, quote=True)
