#!/usr/bin/env python3
"""
Add a comment to an OpenProject work package.

Usage:
    python add-comment.py <wp_id> --comment "Your comment here"
    python add-comment.py <wp_id> --file path/to/comment.md
"""

import argparse
import json
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

CONFIG_PATH = Path(__file__).parent.parent / ".config" / "client-settings.json"
config = json.loads(CONFIG_PATH.read_text())

BASE_URL = config["base_url"]
API_KEY = config["api_key"]
auth = HTTPBasicAuth("apikey", API_KEY)


def add_comment(wp_id: int, markdown: str) -> dict:
    resp = requests.post(
        f"{BASE_URL}/api/v3/work_packages/{wp_id}/activities",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json={"comment": {"raw": markdown}},
    )
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(
        description="Add a comment to an OpenProject work package."
    )
    parser.add_argument("wp_id", type=int, help="Work package ID")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--comment", type=str, help="Comment text (markdown supported)")
    group.add_argument("--file", type=Path, help="Path to a markdown file")

    args = parser.parse_args()

    # Resolve markdown content
    if args.comment is not None:
        if args.comment.strip() == "":
            print("Error: --comment cannot be empty.", file=sys.stderr)
            sys.exit(1)
        markdown = args.comment
    else:
        if not args.file.exists():
            print(f"Error: file '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        markdown = args.file.read_text(encoding="utf-8").strip()
        if not markdown:
            print(f"Error: file '{args.file}' is empty.", file=sys.stderr)
            sys.exit(1)

    # Post the comment
    try:
        result = add_comment(args.wp_id, markdown)
        activity_id = result.get("id", "?")
        print(f"Comment added to WP #{args.wp_id} (activity #{activity_id})")
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()