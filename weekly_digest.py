#!/usr/bin/env python3
"""Post this week's Weekly Cadence tasks from Notion to Slack.

Config comes from environment variables (or a .env file next to this script):
  NOTION_TOKEN         Notion internal integration secret
  SLACK_WEBHOOK_URL    Slack incoming webhook URL
  NOTION_DATA_SOURCE   (optional) Weekly Cadence data source ID
  TIMEZONE             (optional) timezone used to define "this week"

Run with --dry-run to print the message instead of posting it.
"""

import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

NOTION_VERSION = "2025-09-03"
DEFAULT_DATA_SOURCE = "3dbf4187-df96-801b-897c-000b64840a1d"
SUBTEAM_ORDER = ["Mechanical", "Electrical", "Embedded", "Design"]


def load_env_file():
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def request_json(url, payload=None, headers=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers or {}, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode()
    return json.loads(body) if body.startswith("{") else body


def week_bounds(tz):
    today = datetime.now(tz).date()
    monday = today - timedelta(days=today.weekday())
    return monday, monday + timedelta(days=6)


def fetch_tasks(token, data_source, monday, sunday):
    url = f"https://api.notion.com/v1/data_sources/{data_source}/query"
    headers = {"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION}
    payload = {
        "filter": {
            "and": [
                {"property": "Date", "date": {"on_or_after": monday.isoformat()}},
                {"property": "Date", "date": {"on_or_before": sunday.isoformat()}},
                {"property": "Status", "status": {"does_not_equal": "Done"}},
            ]
        },
        "sorts": [{"property": "Date", "direction": "ascending"}],
        "page_size": 100,
    }
    results = []
    while True:
        resp = request_json(url, payload, headers)
        results.extend(resp["results"])
        if not resp.get("has_more"):
            return results
        payload["start_cursor"] = resp["next_cursor"]


def slack_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_task(page):
    props = page["properties"]
    title = "".join(t["plain_text"] for t in props["Name"]["title"]).strip() or "Untitled"
    people = [p.get("name") or "Unknown" for p in props["Assigned To"]["people"]]
    subteam = (props["Subteam"]["select"] or {}).get("name") or "No subteam"
    status = (props["Status"]["status"] or {}).get("name") or ""
    date = (props["Date"]["date"] or {}).get("start", "")[:10]
    return {
        "title": title,
        "url": page["url"],
        "people": people,
        "subteam": subteam,
        "status": status,
        "date": date,
    }


def build_message(tasks, monday, sunday):
    header = f":calendar: *Weekly Cadence: {monday:%b %-d} – {sunday:%b %-d}*"
    if not tasks:
        return f"{header}\n\nNo open tasks scheduled this week. :tada:"

    by_team = defaultdict(list)
    for task in tasks:
        by_team[task["subteam"]].append(task)
    teams = sorted(by_team, key=lambda t: (SUBTEAM_ORDER.index(t) if t in SUBTEAM_ORDER else 99, t))

    lines = [header, f"{len(tasks)} open task{'s' if len(tasks) != 1 else ''} this week:"]
    for team in teams:
        lines.append(f"\n*{team}*")
        for task in by_team[team]:
            day = datetime.fromisoformat(task["date"]).strftime("%a %-m/%-d") if task["date"] else ""
            who = ", ".join(task["people"]) if task["people"] else "_unassigned_"
            link = f"<{task['url']}|{slack_escape(task['title'])}>"
            lines.append(f"• {link}: {slack_escape(who)} · {day} · {task['status']}")
    lines.append("\nUpdate your task status in Notion as you go. Reply in thread if you're blocked.")
    return "\n".join(lines)


def main():
    load_env_file()
    dry_run = "--dry-run" in sys.argv
    token = os.environ.get("NOTION_TOKEN")
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    data_source = os.environ.get("NOTION_DATA_SOURCE", DEFAULT_DATA_SOURCE)
    tz = ZoneInfo(os.environ.get("TIMEZONE", "America/New_York"))

    if not token:
        sys.exit("NOTION_TOKEN is not set")
    if not webhook and not dry_run:
        sys.exit("SLACK_WEBHOOK_URL is not set")

    monday, sunday = week_bounds(tz)
    tasks = [parse_task(p) for p in fetch_tasks(token, data_source, monday, sunday)]
    message = build_message(tasks, monday, sunday)

    if dry_run:
        print(message)
        return
    request_json(webhook, {"text": message, "unfurl_links": False})
    print(f"Posted {len(tasks)} tasks for week of {monday}")


if __name__ == "__main__":
    main()
