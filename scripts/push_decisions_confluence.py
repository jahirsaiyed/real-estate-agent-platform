#!/usr/bin/env python3
"""Push product decisions ADR page to Confluence."""

import io
import os
import re
import sys
import base64
import requests
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CONFLUENCE_BASE = os.environ.get("CONFLUENCE_BASE", "https://jsaiyed.atlassian.net/wiki")
EMAIL           = os.environ.get("ATLASSIAN_EMAIL", "")
API_TOKEN       = os.environ.get("ATLASSIAN_API_TOKEN", "")

if not EMAIL or not API_TOKEN:
    print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables.")
    sys.exit(1)
SPACE_KEY   = "REALESTATEAGENT"
HOMEPAGE_ID = "22708402"
API_BASE    = f"{CONFLUENCE_BASE}/rest/api"
HEADERS     = {
    "Authorization": "Basic " + base64.b64encode(f"{EMAIL}:{API_TOKEN}".encode()).decode(),
    "Content-Type": "application/json",
    "Accept": "application/json",
}

SOURCE = (
    r"C:\Users\jahir\.claude\projects"
    r"\D--Projects-Real-Estate-Agent\memory\product-decisions.md"
)

TITLE = "Product Decisions — Architecture Decision Record"

# ── Markdown → Confluence storage ─────────────────────────────────────────

def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_format(text: str) -> str:
    text = xml_escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`\n]+)`", lambda m: f"<code>{m.group(1)}</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', text)
    return text


PIPE_RE = re.compile(r"(?<!\\)\|")
SEP_RE  = re.compile(r"^\s*\|[\s\-\|:]+\|\s*$")


def table_to_storage(lines: list) -> str:
    rows = [l for l in lines if not SEP_RE.match(l)]
    if not rows:
        return ""
    html = ['<table data-layout="default"><tbody>']
    for idx, line in enumerate(rows):
        cells = [c.strip() for c in PIPE_RE.split(line) if c.strip()]
        tag = "th" if idx == 0 else "td"
        html.append(
            "<tr>" + "".join(f"<{tag}><p>{inline_format(c)}</p></{tag}>" for c in cells) + "</tr>"
        )
    html.append("</tbody></table>")
    return "\n".join(html)


def md_to_storage(md: str) -> str:
    lines = md.split("\n")
    parts = []
    i = 0
    in_ul = in_ol = False

    def close_list():
        nonlocal in_ul, in_ol
        if in_ul:
            parts.append("</ul>")
            in_ul = False
        if in_ol:
            parts.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        # Fenced code block
        if s.startswith("```"):
            close_list()
            lang = s[3:].strip().lower()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            safe = "\n".join(code_lines).replace("]]>", "]] >")
            lp = f'<ac:parameter ac:name="language">{lang}</ac:parameter>' if lang else ""
            parts.append(
                f'<ac:structured-macro ac:name="code" ac:schema-version="1">'
                f'{lp}<ac:plain-text-body><![CDATA[{safe}]]></ac:plain-text-body>'
                f'</ac:structured-macro>'
            )
            i += 1
            continue

        # Table
        if s.startswith("|"):
            close_list()
            tbl_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i])
                i += 1
            parts.append(table_to_storage(tbl_lines))
            continue

        # Heading
        hm = re.match(r"^(#{1,4})\s+(.*)", line)
        if hm:
            close_list()
            lvl = min(len(hm.group(1)), 4)
            parts.append(f"<h{lvl}>{inline_format(hm.group(2))}</h{lvl}>")
            i += 1
            continue

        # HR
        if re.match(r"^[-*=]{3,}\s*$", s) and len(set(s.replace(" ", ""))) == 1:
            close_list()
            parts.append("<hr/>")
            i += 1
            continue

        # Unordered list
        ul_m = re.match(r"^[-*]\s+(.*)", line)
        if ul_m:
            if in_ol:
                close_list()
            if not in_ul:
                parts.append("<ul>")
                in_ul = True
            parts.append(f"<li><p>{inline_format(ul_m.group(1))}</p></li>")
            i += 1
            continue

        # Ordered list
        ol_m = re.match(r"^\d+\.\s+(.*)", line)
        if ol_m:
            if in_ul:
                close_list()
            if not in_ol:
                parts.append("<ol>")
                in_ol = True
            parts.append(f"<li><p>{inline_format(ol_m.group(1))}</p></li>")
            i += 1
            continue

        # Empty line
        if s == "":
            close_list()
            i += 1
            continue

        # Paragraph
        close_list()
        parts.append(f"<p>{inline_format(line)}</p>")
        i += 1

    close_list()
    return "\n".join(parts)


# ── API helpers ────────────────────────────────────────────────────────────

def get_page(title: str):
    r = requests.get(
        f"{API_BASE}/content", headers=HEADERS,
        params={"title": title, "spaceKey": SPACE_KEY, "expand": "version"},
        timeout=30,
    )
    r.raise_for_status()
    results = r.json().get("results", [])
    return results[0] if results else None


def upsert(title: str, body: str) -> str:
    existing = get_page(title)
    if existing:
        pid = existing["id"]
        ver = existing["version"]["number"]
        print(f"Updating '{title}' (v{ver} -> v{ver + 1})")
        r = requests.put(
            f"{API_BASE}/content/{pid}", headers=HEADERS, timeout=30,
            json={
                "type": "page", "title": title,
                "version": {"number": ver + 1},
                "body": {"storage": {"value": body, "representation": "storage"}},
            },
        )
    else:
        print(f"Creating '{title}'")
        r = requests.post(
            f"{API_BASE}/content", headers=HEADERS, timeout=30,
            json={
                "type": "page", "title": title,
                "space": {"key": SPACE_KEY},
                "ancestors": [{"id": HOMEPAGE_ID}],
                "body": {"storage": {"value": body, "representation": "storage"}},
            },
        )
    if not r.ok:
        print(f"FAILED {r.status_code}: {r.text[:400]}")
        r.raise_for_status()
    return r.json()["id"]


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    md   = Path(SOURCE).read_text(encoding="utf-8")
    body = md_to_storage(md)
    pid  = upsert(TITLE, body)
    print(f"OK -> {CONFLUENCE_BASE}/spaces/{SPACE_KEY}/pages/{pid}")


if __name__ == "__main__":
    main()
