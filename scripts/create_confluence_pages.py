#!/usr/bin/env python3
"""
create_confluence_pages.py
Push technical architecture docs to Confluence REALESTATEAGENT space.

Usage:
    python scripts/create_confluence_pages.py
"""

import io
import os
import re
import sys
import base64
import requests
from pathlib import Path

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Config ────────────────────────────────────────────────────────────────────
CONFLUENCE_BASE = os.environ.get("CONFLUENCE_BASE", "https://jsaiyed.atlassian.net/wiki")
EMAIL           = os.environ.get("ATLASSIAN_EMAIL", "")
API_TOKEN       = os.environ.get("ATLASSIAN_API_TOKEN", "")

if not EMAIL or not API_TOKEN:
    print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables.")
    sys.exit(1)
SPACE_KEY       = "REALESTATEAGENT"
DOCS_DIR        = Path(__file__).parent.parent / "docs" / "architecture"
API_BASE        = f"{CONFLUENCE_BASE}/rest/api"

HEADERS = {
    "Authorization": "Basic " + base64.b64encode(f"{EMAIL}:{API_TOKEN}".encode()).decode(),
    "Content-Type":  "application/json",
    "Accept":        "application/json",
}

PAGES = [
    ("01 - System Overview",         "01-system-overview.md"),
    ("02 - C4 Container Diagram",    "02-c4-containers.md"),
    ("03 - Component Diagram",       "03-component-diagram.md"),
    ("04 - Sequence Diagrams",       "04-sequence-diagrams.md"),
    ("05 - Data Flow",               "05-data-flow.md"),
    ("06 - Deployment Architecture", "06-deployment.md"),
    ("07 - Database Schema",         "07-database-schema.md"),
    ("08 - API Design",              "08-api-design.md"),
    ("09 - Agent Architecture",      "09-agent-architecture.md"),
]

# ── Markdown → Confluence Storage Format ─────────────────────────────────────

def xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline_format(text: str) -> str:
    text = xml_escape(text)
    # Bold (**text**)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic (*text*) — avoid matching inside bold
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    # Inline code (`text`)
    text = re.sub(r"`([^`\n]+)`", lambda m: f"<code>{m.group(1)}</code>", text)
    # Links [label](url)
    text = re.sub(r"\[([^\]]+)\]\(([^\)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def code_macro(lang: str, code: str) -> str:
    safe = code.replace("]]>", "]] >")
    lang_param = f'<ac:parameter ac:name="language">{lang}</ac:parameter>' if lang and lang != "text" else ""
    return (
        '<ac:structured-macro ac:name="code" ac:schema-version="1">'
        f'{lang_param}'
        '<ac:parameter ac:name="collapse">false</ac:parameter>'
        f'<ac:plain-text-body><![CDATA[{safe}]]></ac:plain-text-body>'
        '</ac:structured-macro>'
    )


def table_to_storage(lines: list) -> str:
    # Skip pure separator rows (|---|---|)
    rows = [l for l in lines if not re.match(r"^\s*\|[\s\-\|:]+\|\s*$", l)]
    if not rows:
        return ""
    html = ['<table data-layout="default"><tbody>']
    for idx, line in enumerate(rows):
        # Split on | but not escaped \|
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line) if c.strip() != ""]
        tag = "th" if idx == 0 else "td"
        cells_html = "".join(f"<{tag}><p>{inline_format(c)}</p></{tag}>" for c in cells)
        html.append(f"<tr>{cells_html}</tr>")
    html.append("</tbody></table>")
    return "\n".join(html)


def md_to_storage(md: str) -> str:
    lines = md.split("\n")
    parts = []
    i = 0
    in_ul = False
    in_ol = False

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
        stripped = line.strip()

        # ── Fenced code block (``` lang) ──────────────────────────────────
        if stripped.startswith("```"):
            close_list()
            lang = stripped[3:].strip().lower()
            # Normalize common aliases
            lang = {"js": "javascript", "py": "python", "sh": "bash",
                    "yml": "yaml", "": "text"}.get(lang, lang)
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            parts.append(code_macro(lang, "\n".join(code_lines)))
            i += 1
            continue

        # ── Table (line starts with |) ─────────────────────────────────────
        if stripped.startswith("|"):
            close_list()
            tbl = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            parts.append(table_to_storage(tbl))
            continue  # i already advanced

        # ── Heading (# ## ### ####) ────────────────────────────────────────
        hm = re.match(r"^(#{1,4})\s+(.*)", line)
        if hm:
            close_list()
            lvl = min(len(hm.group(1)), 4)
            parts.append(f"<h{lvl}>{inline_format(hm.group(2))}</h{lvl}>")
            i += 1
            continue

        # ── Horizontal rule ────────────────────────────────────────────────
        if re.match(r"^[-*=]{3,}\s*$", stripped) and len(set(stripped.replace(" ", ""))) == 1:
            close_list()
            parts.append("<hr/>")
            i += 1
            continue

        # ── Unordered list item (- or *) ───────────────────────────────────
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

        # ── Ordered list item (1. 2. etc) ─────────────────────────────────
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

        # ── Empty line ─────────────────────────────────────────────────────
        if stripped == "":
            close_list()
            i += 1
            continue

        # ── Paragraph ─────────────────────────────────────────────────────
        close_list()
        parts.append(f"<p>{inline_format(line)}</p>")
        i += 1

    close_list()
    return "\n".join(parts)


# ── Confluence API helpers ────────────────────────────────────────────────────

def api_get(path: str, params: dict = None) -> dict:
    r = requests.get(f"{API_BASE}{path}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def api_post(path: str, data: dict) -> dict:
    r = requests.post(f"{API_BASE}{path}", headers=HEADERS, json=data, timeout=30)
    if not r.ok:
        print(f"    ERROR {r.status_code}: {r.text[:500]}")
        r.raise_for_status()
    return r.json()


def api_put(path: str, data: dict) -> dict:
    r = requests.put(f"{API_BASE}{path}", headers=HEADERS, json=data, timeout=30)
    if not r.ok:
        print(f"    ERROR {r.status_code}: {r.text[:500]}")
        r.raise_for_status()
    return r.json()


def get_page_by_title(title: str) -> dict | None:
    result = api_get("/content", params={
        "title": title, "spaceKey": SPACE_KEY, "expand": "version"
    })
    pages = result.get("results", [])
    return pages[0] if pages else None


def create_page(title: str, body: str, parent_id: str = None) -> dict:
    data = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    if parent_id:
        data["ancestors"] = [{"id": parent_id}]
    return api_post("/content", data)


def update_page(page_id: str, title: str, body: str, version: int) -> dict:
    return api_put(f"/content/{page_id}", {
        "type": "page",
        "title": title,
        "version": {"number": version + 1},
        "body": {"storage": {"value": body, "representation": "storage"}},
    })


def upsert_page(title: str, body: str, parent_id: str = None) -> str:
    existing = get_page_by_title(title)
    if existing:
        pid = existing["id"]
        ver = existing["version"]["number"]
        print(f"    Updating '{title}' (v{ver} → v{ver + 1})")
        result = update_page(pid, title, body, ver)
    else:
        print(f"    Creating '{title}'")
        result = create_page(title, body, parent_id)
    return result["id"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"Connecting to Confluence space '{SPACE_KEY}'...")
    try:
        space = api_get(f"/space/{SPACE_KEY}", {"expand": "homepage"})
        homepage_id = space.get("homepage", {}).get("id")
        print(f"  Space: {space['name']}  |  Homepage ID: {homepage_id}")
    except requests.HTTPError as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    # Parent page
    print("\nEnsuring 'Technical Architecture' parent page...")
    parent_body = (
        "<p>System design documentation for the <strong>Real Estate Agent Platform</strong> "
        "(Dubai/UAE). Covers architecture, data flows, deployment, database, API, and AI agent design.</p>"
        "<p><em>All diagrams use Mermaid syntax. To render: paste into "
        '<a href="https://mermaid.live">mermaid.live</a> or install the '
        "Mermaid app from the Atlassian Marketplace.</em></p>"
        "<h2>Documents</h2>"
        "<table data-layout='default'><tbody>"
        "<tr><th><p>#</p></th><th><p>Page</p></th><th><p>Contents</p></th></tr>"
        "<tr><td><p>01</p></td><td><p>System Overview</p></td><td><p>C4 Context diagram, architecture layers, design principles</p></td></tr>"
        "<tr><td><p>02</p></td><td><p>C4 Container Diagram</p></td><td><p>All deployable units and inter-container communication</p></td></tr>"
        "<tr><td><p>03</p></td><td><p>Component Diagram</p></td><td><p>FastAPI services, LangGraph agent graph, frontend, adapter pattern</p></td></tr>"
        "<tr><td><p>04</p></td><td><p>Sequence Diagrams</p></td><td><p>6 flows: qualification, search, booking, handoff, RAG, ETL</p></td></tr>"
        "<tr><td><p>05</p></td><td><p>Data Flow</p></td><td><p>Ingestion pipeline, memory architecture, ETL schedule</p></td></tr>"
        "<tr><td><p>06</p></td><td><p>Deployment Architecture</p></td><td><p>MVP (Render+Vercel) and Production (AWS UAE) topologies</p></td></tr>"
        "<tr><td><p>07</p></td><td><p>Database Schema</p></td><td><p>ERD with 20+ tables, indexes, design decisions</p></td></tr>"
        "<tr><td><p>08</p></td><td><p>API Design</p></td><td><p>Full REST API reference, auth, versioning, webhooks</p></td></tr>"
        "<tr><td><p>09</p></td><td><p>Agent Architecture</p></td><td><p>LangGraph state machine, tool registry, LLM abstraction</p></td></tr>"
        "</tbody></table>"
    )
    parent_id = upsert_page("Technical Architecture", parent_body, homepage_id)
    print(f"  Parent ID: {parent_id}")

    # Child pages
    print(f"\nPushing {len(PAGES)} documentation pages...")
    results = []
    errors  = []

    for title, filename in PAGES:
        filepath = DOCS_DIR / filename
        if not filepath.exists():
            print(f"\n  SKIP — file not found: {filepath}")
            errors.append(title)
            continue

        print(f"\n  [{filename}]")
        md = filepath.read_text(encoding="utf-8")
        storage = md_to_storage(md)

        try:
            page_id = upsert_page(title, storage, parent_id)
            url = f"{CONFLUENCE_BASE}/spaces/{SPACE_KEY}/pages/{page_id}"
            results.append((title, url))
            print(f"    OK → {url}")
        except Exception as e:
            print(f"    FAILED: {e}")
            errors.append(title)

    # Summary
    print(f"\n{'='*65}")
    print(f"Done: {len(results)} pages created/updated, {len(errors)} errors")
    print(f"\nParent page:")
    print(f"  {CONFLUENCE_BASE}/spaces/{SPACE_KEY}/pages/{parent_id}")
    if results:
        print(f"\nPages:")
        for title, url in results:
            print(f"  {title}")
            print(f"    {url}")
    if errors:
        print(f"\nFailed:")
        for t in errors:
            print(f"  - {t}")


if __name__ == "__main__":
    main()
