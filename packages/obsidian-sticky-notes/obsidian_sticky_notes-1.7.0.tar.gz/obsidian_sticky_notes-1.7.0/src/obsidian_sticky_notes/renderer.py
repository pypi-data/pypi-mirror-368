import re, pathlib, frontmatter
from markdown_it import MarkdownIt
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.attrs import attrs_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
try:
  from mdit_py_plugins.emoji import emoji_plugin; _HAS_EMOJI=True
except Exception:
  _HAS_EMOJI=False
  def emoji_plugin(*a, **k): return lambda md: None

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
CALLOUT_RE = re.compile(r"^>\s*\[!([a-zA-Z]+)\]\s*(.*)$")

def preprocess_obsidian(text: str) -> str:
  lines = text.splitlines(); out = []; in_callout=False
  for ln in lines:
    m = CALLOUT_RE.match(ln)
    if m and not in_callout:
      in_callout=True; kind=m.group(1).lower(); title=m.group(2).strip()
      out.append(f"> <div class=callout callout-{kind}>")
      if title: out.append(f"> <div class=callout-title>{title}</div>")
      continue
    if in_callout:
      if ln.startswith("> ") or ln.startswith(">"):
        stripped = ln[1:].lstrip(); out.append(f"> {stripped}"); continue
      else:
        out.append(">"); out.append(""); in_callout=False
    out.append(ln)
  if in_callout: out.append(">"); out.append("")
  return "\n".join(out)

def wikilink_sub(m):
  target = m.group(1).strip(); label = (m.group(2) or target).strip()
  return f"<a href='#' data-wiki='{target}'>{label}</a>"

md = (MarkdownIt("commonmark", {"html": True})
      .enable(["table", "strikethrough"])
      .use(tasklists_plugin, enabled=True)
      .use(footnote_plugin)
      .use(attrs_plugin)
      .use(emoji_plugin))

def render_markdown_to_html(note_path: pathlib.Path):
  post = frontmatter.load(note_path)
  content = preprocess_obsidian(post.content)
  html = md.render(content)
  html = WIKILINK_RE.sub(wikilink_sub, html)
  return html, (post.metadata or {})
