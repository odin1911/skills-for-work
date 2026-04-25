#!/usr/bin/env python3

import base64
import html
import mimetypes
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / "marc.md"
TARGET_HTML_FILE = BASE_DIR / "marc-share.html"
TARGET_PDF_FILE = BASE_DIR / "marc-share.pdf"

BROWSER_CANDIDATES = [
  Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
  Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ORDERED_RE = re.compile(r"^\d+\.\s+(.*)$")
UNORDERED_RE = re.compile(r"^-\s+(.*)$")
IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$")
URL_RE = re.compile(r"https?://[^\s<]+")


def render_plain(text):
    pieces = []
    last_index = 0
    for match in URL_RE.finditer(text):
        pieces.append(html.escape(text[last_index:match.start()]))
        url = match.group(0)
        safe_url = html.escape(url, quote=True)
        pieces.append('<a href="{0}">{1}</a>'.format(safe_url, html.escape(url)))
        last_index = match.end()
    pieces.append(html.escape(text[last_index:]))
    return "".join(pieces)


def render_inline(text):
    parts = text.split("`")
    rendered = []
    for index, part in enumerate(parts):
        if index % 2 == 1:
            rendered.append("<code>{}</code>".format(html.escape(part)))
        else:
            rendered.append(render_plain(part))
    return "".join(rendered)


def image_data_uri(relative_path):
    image_path = (BASE_DIR / relative_path).resolve()
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        mime_type = "application/octet-stream"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return "data:{};base64,{}".format(mime_type, data)


def paragraph_html(lines):
    text = "<br>".join(render_inline(line.strip()) for line in lines)
    return "<p>{}</p>".format(text)


def list_html(tag_name, items):
    parts = ["<{}>".format(tag_name)]
    for item in items:
        parts.append("<li>{}</li>".format(render_inline(item)))
    parts.append("</{}>".format(tag_name))
    return "".join(parts)


def code_block_html(code_lines):
    return "<pre><code>{}</code></pre>".format(html.escape("\n".join(code_lines)))


def image_html(alt_text, relative_path):
    data_uri = image_data_uri(relative_path)
    return '<p class="image"><img alt="{}" src="{}"></p>'.format(
        html.escape(alt_text, quote=True),
        data_uri,
    )


def render_markdown(lines):
    output = []
    paragraph_lines = []
    unordered_items = []
    ordered_items = []
    in_code_block = False
    code_lines = []

    def flush_paragraph():
        if paragraph_lines:
            output.append(paragraph_html(paragraph_lines))
            paragraph_lines[:] = []

    def flush_unordered():
        if unordered_items:
            output.append(list_html("ul", unordered_items))
            unordered_items[:] = []

    def flush_ordered():
        if ordered_items:
            output.append(list_html("ol", ordered_items))
            ordered_items[:] = []

    def flush_all_text():
        flush_paragraph()
        flush_unordered()
        flush_ordered()

    for raw_line in lines:
        line = raw_line.rstrip("\n")

        if in_code_block:
            if line.startswith("```"):
                output.append(code_block_html(code_lines))
                code_lines = []
                in_code_block = False
            else:
                code_lines.append(line)
            continue

        if line.startswith("```"):
            flush_all_text()
            in_code_block = True
            code_lines = []
            continue

        stripped = line.strip()
        if not stripped:
            flush_all_text()
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            flush_all_text()
            level = len(heading_match.group(1))
            output.append(
                "<h{0}>{1}</h{0}>".format(level, render_inline(heading_match.group(2)))
            )
            continue

        image_match = IMAGE_RE.match(stripped)
        if image_match:
            flush_all_text()
            output.append(image_html(image_match.group(1), image_match.group(2)))
            continue

        unordered_match = UNORDERED_RE.match(stripped)
        if unordered_match:
            flush_paragraph()
            flush_ordered()
            unordered_items.append(unordered_match.group(1))
            continue

        ordered_match = ORDERED_RE.match(stripped)
        if ordered_match:
            flush_paragraph()
            flush_unordered()
            ordered_items.append(ordered_match.group(1))
            continue

        flush_unordered()
        flush_ordered()
        paragraph_lines.append(line)

    if in_code_block:
        output.append(code_block_html(code_lines))
    flush_all_text()
    return "\n".join(output)


def build_html(document_html, title):
    return """<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <style>
    :root {{
      --page-width: 920px;
      --text: #1f2937;
      --muted: #6b7280;
      --border: #d1d5db;
      --surface: #ffffff;
      --surface-alt: #f3f4f6;
      --bg: #eef1f5;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.75 -apple-system, BlinkMacSystemFont, \"Helvetica Neue\", \"PingFang SC\", \"Hiragino Sans GB\", \"Microsoft YaHei\", sans-serif;
    }}

    main {{
      max-width: var(--page-width);
      margin: 32px auto;
      padding: 48px 56px;
      background: var(--surface);
      box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
    }}

    h1, h2, h3, h4, h5, h6 {{
      margin: 1.5em 0 0.6em;
      line-height: 1.3;
      color: #111827;
      page-break-after: avoid;
    }}

    h1 {{ margin-top: 0; font-size: 2rem; }}
    h2 {{ font-size: 1.45rem; padding-top: 0.2rem; border-top: 1px solid var(--border); }}
    h3 {{ font-size: 1.15rem; }}

    p {{ margin: 0.8em 0; }}

    ul, ol {{
      margin: 0.6em 0 1em;
      padding-left: 1.5em;
    }}

    li {{ margin: 0.35em 0; }}

    pre {{
      margin: 1em 0;
      padding: 16px 18px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid var(--border);
      background: var(--surface-alt);
      border-radius: 8px;
      font: 13px/1.6 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}

    code {{
      padding: 0.1em 0.35em;
      border-radius: 4px;
      background: var(--surface-alt);
      font: 0.92em ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}

    pre code {{
      padding: 0;
      background: transparent;
      border-radius: 0;
      font: inherit;
    }}

    a {{ color: inherit; }}

    .image {{
      margin: 1.25em 0;
      page-break-inside: avoid;
    }}

    img {{
      display: block;
      max-width: 100%;
      height: auto;
      margin: 0 auto;
      border: 1px solid var(--border);
    }}

    @page {{
      margin: 16mm;
    }}

    @media print {{
      body {{ background: #fff; }}
      main {{
        max-width: none;
        margin: 0;
        padding: 0;
        box-shadow: none;
      }}
      a {{ text-decoration: none; }}
    }}
  </style>
</head>
<body>
  <main>
{body}
  </main>
</body>
</html>
""".format(title=html.escape(title, quote=True), body=document_html)


def find_browser_binary():
  for browser_path in BROWSER_CANDIDATES:
    if browser_path.exists():
      return browser_path

  for browser_name in ["google-chrome", "chromium", "microsoft-edge"]:
    browser_path = shutil.which(browser_name)
    if browser_path:
      return Path(browser_path)

  raise RuntimeError(
    "Missing browser for PDF export. Install Google Chrome or Microsoft Edge."
  )


def build_pdf(html_file, pdf_file):
  browser_binary = find_browser_binary()
  with tempfile.TemporaryDirectory(prefix="marc-share-") as temp_dir:
    command = [
      str(browser_binary),
      "--headless=new",
      "--disable-gpu",
      "--no-pdf-header-footer",
      "--user-data-dir={}".format(temp_dir),
      "--print-to-pdf={}".format(pdf_file),
      html_file.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
  lines = SOURCE_FILE.read_text(encoding="utf-8").splitlines()
  title = "marc 功能"
  if lines and lines[0].startswith("# "):
    title = lines[0][2:].strip()
  document_html = render_markdown(lines)
  TARGET_HTML_FILE.write_text(build_html(document_html, title), encoding="utf-8")
  build_pdf(TARGET_HTML_FILE, TARGET_PDF_FILE)
  print("Generated {}".format(TARGET_HTML_FILE))
  print("Generated {}".format(TARGET_PDF_FILE))


if __name__ == "__main__":
    main()