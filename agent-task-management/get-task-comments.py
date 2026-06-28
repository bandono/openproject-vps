#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
import sys

import requests
from requests.auth import HTTPBasicAuth

CONFIG_PATH = Path(__file__).parent.parent / ".config" / "client-settings.json"
LANE_PATH = Path(__file__).parent / "board-settings.json"

config = json.loads(CONFIG_PATH.read_text())
LANES = json.loads(LANE_PATH.read_text())

BASE_URL = config["base_url"]
API_KEY = config["api_key"]

auth = HTTPBasicAuth("apikey", API_KEY)

def get_comments(wp_id: int) -> None:
    resp = requests.get(
        f"{BASE_URL}/api/v3/work_packages/{wp_id}/activities",
        auth=auth,
    )
    resp.raise_for_status()

    activities = resp.json()["_embedded"]["elements"]
    comments = [a for a in activities if a.get("comment", {}).get("raw", "").strip()]

    if not comments:
        print("No comments found.")
        return

    for c in comments:
        author = c["_links"]["user"]
        created_at = c["createdAt"]
        raw = c["comment"]["raw"]
        print(f"--- #{c['id']} by {author} at {created_at} ---")
        print(raw)
        print()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "wp_id",
        type=int,
        help="Work package ID",
    )

    args = parser.parse_args()

    try:
        get_comments(args.wp_id)

    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)



if __name__ == "__main__":
    main()