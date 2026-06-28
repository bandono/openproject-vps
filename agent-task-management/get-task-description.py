#!/usr/bin/env python3

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

def get_description(wp_id: int) -> str:
    """
    Get the raw markdown description of a work package.
    """
    resp = requests.get(
        f"{BASE_URL}/api/v3/work_packages/{wp_id}",
        auth=auth,
    )
    resp.raise_for_status()
    print(resp.json()["description"]["raw"])

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "wp_id",
        type=int,
        help="Work package ID",
    )

    args = parser.parse_args()

    try:
        get_description(wp_id=args.wp_id)
    except requests.HTTPError as e:
        print(f"Error {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()