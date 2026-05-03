#!/usr/bin/env python3
"""
setup_sprints.py
================
Create 6 sprints for the REA project aligned with the 5 roadmap phases,
then assign all 51 stories (and their subtasks) to the correct sprint.

Sprint layout (3-week sprints, start: 2026-05-03):
  Sprint 1  – Phase 1: Foundation & Infrastructure          (Wk  1-3)
  Sprint 2  – Phase 2: Core Agent & Property Features       (Wk  4-6)
  Sprint 3  – Phase 3: Intelligence Layer & Content         (Wk  7-9)
  Sprint 4  – Phase 4: Production Hardening                 (Wk 10-12)
  Sprint 5  – Phase 5a: Adapters & Expansion (first half)   (Wk 13-15)
  Sprint 6  – Phase 5b: Adapters & Expansion (second half)  (Wk 16-18)

Usage:
    python scripts/setup_sprints.py
"""

import os, sys, time, requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────
JIRA_BASE  = os.environ.get("JIRA_BASE",            "https://jsaiyed.atlassian.net")
EMAIL      = os.environ.get("ATLASSIAN_EMAIL",       "")
TOKEN      = os.environ.get("ATLASSIAN_API_TOKEN",   "")
BOARD_ID   = 2
PROJECT    = "REA"
DELAY      = 0.3   # seconds between API calls

if not EMAIL or not TOKEN:
    print("ERROR: Set ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN environment variables.")
    sys.exit(1)

AUTH    = HTTPBasicAuth(EMAIL, TOKEN)
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# ── Sprint definitions ─────────────────────────────────────────────────────────
# Start date: 2026-05-03 (today), 3-week sprints
START = datetime(2026, 5, 3)

def sprint_dates(sprint_number: int):
    """Return (start, end) ISO date strings for a 3-week sprint."""
    start = START + timedelta(weeks=3 * (sprint_number - 1))
    end   = start + timedelta(weeks=3) - timedelta(days=1)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

SPRINT_DEFS = [
    {
        "number": 1,
        "name": "Sprint 1 – Phase 1: Foundation & Infrastructure",
        "goal": "Deliver working monorepo, CI/CD pipeline, all cloud services connected, "
                "FastAPI skeleton, LLM abstraction, LangGraph orchestrator, and Next.js admin shell.",
        "stories": [
            "REA-2",  "REA-9",  "REA-17", "REA-25", "REA-32", "REA-41", "REA-48",
        ],
    },
    {
        "number": 2,
        "name": "Sprint 2 – Phase 2: Core Agent & Property Features",
        "goal": "Deliver property search, booking, CRM adapters, conversation memory, RAG pipeline, "
                "web chat widget, listing pages, search UI, WhatsApp/Telegram channels, and notifications.",
        "stories": [
            "REA-55",  "REA-63",  "REA-70",  "REA-77",  "REA-85",
            "REA-92",  "REA-100", "REA-108", "REA-117", "REA-125", "REA-133",
        ],
    },
    {
        "number": 3,
        "name": "Sprint 3 – Phase 3: Intelligence Layer & Content",
        "goal": "Deliver lead qualification engine, sentiment analysis, guardrails, calculators, "
                "ETL adapters, Celery scheduler, dashboards, multilingual UI (AR/HI/RU), PWA, "
                "document management, LLM translation, and UTM tracking.",
        "stories": [
            "REA-140", "REA-148", "REA-155", "REA-164", "REA-173",
            "REA-181", "REA-189", "REA-196", "REA-203", "REA-210",
            "REA-217", "REA-224", "REA-231",
        ],
    },
    {
        "number": 4,
        "name": "Sprint 4 – Phase 4: Production Hardening",
        "goal": "Deliver off-plan EOI, broker API adapters, e-signatures, event-driven workflows, "
                "full observability stack, content pages, reports, public API docs, load testing "
                "at 500 concurrent conversations, and Kubernetes manifests.",
        "stories": [
            "REA-238", "REA-244", "REA-250", "REA-256", "REA-262", "REA-269",
            "REA-277", "REA-284", "REA-291", "REA-297", "REA-304", "REA-311",
        ],
    },
    {
        "number": 5,
        "name": "Sprint 5 – Phase 5a: Additional Integrations",
        "goal": "Deliver Salesforce/Propspace/Masterkey CRM adapters, RERA transaction data, "
                "Dubizzle feed, and Mandarin/French/German language support.",
        "stories": [
            "REA-318", "REA-324", "REA-330", "REA-335",
        ],
    },
    {
        "number": 6,
        "name": "Sprint 6 – Phase 5b: Platform Expansion",
        "goal": "Deliver full Arabic admin panel, Microsoft Outlook calendar adapter, "
                "live UAE bank mortgage rate integration, and React Native app scaffold.",
        "stories": [
            "REA-340", "REA-345", "REA-351", "REA-357",
        ],
    },
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_all_issues():
    """Fetch all issues (stories + subtasks) from REA project."""
    all_issues = []
    body = {
        "jql": "project = REA ORDER BY key ASC",
        "maxResults": 100,
        "fields": ["summary", "issuetype", "parent"],
    }
    while True:
        r = requests.post(f"{JIRA_BASE}/rest/api/3/search/jql", auth=AUTH, headers=HEADERS, json=body)
        r.raise_for_status()
        data = r.json()
        all_issues.extend(data.get("issues", []))
        if data.get("isLast", True) or not data.get("issues"):
            break
        body["nextPageToken"] = data["nextPageToken"]
    return all_issues


def get_existing_sprints():
    """Return dict of sprint name → sprint id for existing sprints on BOARD_ID."""
    r = requests.get(
        f"{JIRA_BASE}/rest/agile/1.0/board/{BOARD_ID}/sprint",
        auth=AUTH, headers=HEADERS,
    )
    r.raise_for_status()
    return {s["name"]: s["id"] for s in r.json().get("values", [])}


def create_sprint(name, goal, start_date, end_date):
    payload = {
        "name": name,
        "goal": goal,
        "startDate": f"{start_date}T00:00:00.000Z",
        "endDate":   f"{end_date}T23:59:59.000Z",
        "originBoardId": BOARD_ID,
    }
    r = requests.post(
        f"{JIRA_BASE}/rest/agile/1.0/sprint",
        auth=AUTH, headers=HEADERS, json=payload,
    )
    if not r.ok:
        print(f"  WARN create_sprint '{name}': {r.status_code} {r.text[:200]}")
        return None
    return r.json()["id"]


def update_sprint(sprint_id, name, goal, start_date, end_date):
    payload = {
        "name": name,
        "goal": goal,
        "startDate": f"{start_date}T00:00:00.000Z",
        "endDate":   f"{end_date}T23:59:59.000Z",
    }
    r = requests.put(
        f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id}",
        auth=AUTH, headers=HEADERS, json=payload,
    )
    if not r.ok:
        print(f"  WARN update_sprint {sprint_id}: {r.status_code} {r.text[:200]}")


def move_issues_to_sprint(sprint_id, issue_keys):
    """Move a batch of issues to a sprint (max 50 per call)."""
    batch_size = 50
    for i in range(0, len(issue_keys), batch_size):
        batch = issue_keys[i : i + batch_size]
        r = requests.post(
            f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id}/issue",
            auth=AUTH, headers=HEADERS,
            json={"issues": batch},
        )
        if not r.ok:
            print(f"  WARN move to sprint {sprint_id}: {r.status_code} {r.text[:200]}")
        time.sleep(DELAY)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("  REA Sprint Setup")
    print("=" * 65)

    # 1. Fetch all issues to build parent → children map
    print("\n[1/4] Fetching all REA issues...")
    all_issues = get_all_issues()
    print(f"  Found {len(all_issues)} total issues")

    # Build story key → list of subtask keys
    subtask_map: dict[str, list[str]] = {}
    for issue in all_issues:
        if issue["fields"]["issuetype"]["name"] == "Subtask":
            parent_key = issue["fields"].get("parent", {}).get("key")
            if parent_key:
                subtask_map.setdefault(parent_key, []).append(issue["key"])

    print(f"  Stories with subtasks: {len(subtask_map)}")

    # 2. Get / create sprints
    print("\n[2/4] Setting up sprints...")
    existing = get_existing_sprints()
    sprint_id_map: dict[int, int] = {}  # sprint_number → sprint_id

    # The first sprint already exists as "REA Sprint 1" — find it
    existing_sprint1_id = None
    for name, sid in existing.items():
        if "Sprint 1" in name or name.strip() == "REA Sprint 1":
            existing_sprint1_id = sid
            break

    for defn in SPRINT_DEFS:
        n = defn["number"]
        name = defn["name"]
        goal = defn["goal"]
        start, end = sprint_dates(n)

        if n == 1 and existing_sprint1_id:
            print(f"  Updating  Sprint {n} (id={existing_sprint1_id}): {start} → {end}")
            update_sprint(existing_sprint1_id, name, goal, start, end)
            sprint_id_map[n] = existing_sprint1_id
        elif name in existing:
            print(f"  Exists    Sprint {n} (id={existing[name]}): skipping create")
            sprint_id_map[n] = existing[name]
        else:
            print(f"  Creating  Sprint {n}: {start} → {end}")
            sid = create_sprint(name, goal, start, end)
            if sid:
                sprint_id_map[n] = sid
                print(f"            → id={sid}")
            time.sleep(DELAY)

    print(f"\n  Sprint IDs: {sprint_id_map}")

    # 3. Assign stories (+ their subtasks) to sprints
    print("\n[3/4] Assigning issues to sprints...")
    total_moved = 0

    for defn in SPRINT_DEFS:
        n = defn["number"]
        sprint_id = sprint_id_map.get(n)
        if not sprint_id:
            print(f"  SKIP Sprint {n} – no sprint id")
            continue

        stories = defn["stories"]
        all_keys = list(stories)  # stories first

        # Add subtasks for each story
        for s in stories:
            all_keys.extend(subtask_map.get(s, []))

        print(f"  Sprint {n}: moving {len(stories)} stories + {len(all_keys)-len(stories)} subtasks "
              f"= {len(all_keys)} issues")
        move_issues_to_sprint(sprint_id, all_keys)
        total_moved += len(all_keys)

    print(f"\n  Total issues assigned: {total_moved}")

    # 4. Summary
    print("\n[4/4] Summary")
    print("-" * 65)
    for defn in SPRINT_DEFS:
        n = defn["number"]
        start, end = sprint_dates(n)
        sid = sprint_id_map.get(n, "???")
        stories = defn["stories"]
        subtask_count = sum(len(subtask_map.get(s, [])) for s in stories)
        print(f"  Sprint {n} (id={sid}) [{start} → {end}]")
        print(f"    {defn['name']}")
        print(f"    {len(stories)} stories, {subtask_count} subtasks")
    print("-" * 65)
    print("Done! Open the board at: https://jsaiyed.atlassian.net/jira/software/projects/REA/boards")


if __name__ == "__main__":
    main()
