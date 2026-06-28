#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

CONFIG_PATH = Path(__file__).parent.parent / ".config" / "client-settings.json"

config = json.loads(CONFIG_PATH.read_text())

BASE_URL = config["base_url"]
API_KEY = config["api_key"]

auth = HTTPBasicAuth("apikey", API_KEY)

def parse_markdown(md_file: Path):
    """
    First markdown heading becomes subject.
    Remaining content becomes description.
    """

    text = md_file.read_text(encoding="utf-8").strip()

    lines = text.splitlines()

    subject = None
    body_start = 0

    for i, line in enumerate(lines):
        if line.strip().startswith("#"):
            subject = line.lstrip("#").strip()
            body_start = i + 1
            break

    if not subject:
        raise ValueError(
            "Markdown file must start with a heading (# Subject)"
        )

    description = "\n".join(lines[body_start:]).strip()

    return subject, description

def update_description(wp_id: int, subject: str, description: str) -> dict:
    # Must fetch lockVersion first to avoid conflict errors
    wp = requests.get(f"{BASE_URL}/api/v3/work_packages/{wp_id}", auth=auth).json()

    resp = requests.patch(
        f"{BASE_URL}/api/v3/work_packages/{wp_id}",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json={
            "lockVersion": wp["lockVersion"],
            "subject": subject,
            "description": {"raw": description},
        },
    )
    resp.raise_for_status()
    return resp.json()

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "wp_id",
        type=int,
        help="Work package ID",
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Markdown task file"
    )


    args = parser.parse_args()

    subject, description = parse_markdown(
        Path(args.file)
    )

    result = update_description(
        wp_id=args.wp_id,
        subject=subject,
        description=description,
    )

    print(
        f"Updated WP #{args.wp_id}"
    )

if __name__ == "__main__":
    main()