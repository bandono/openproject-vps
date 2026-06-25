#!/usr/bin/env python3

import argparse
import json
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

CONFIG_PATH = Path(__file__).parent.parent / ".config" / "client-settings.json"

config = json.loads(CONFIG_PATH.read_text())

BASE_URL = config["base_url"]
API_KEY = config["api_key"]

auth = HTTPBasicAuth("apikey", API_KEY)

def get_my_work_packages(user_id: int, project_id: int = None) -> list[dict]:
    """
    Get all work packages assigned to a specific user.
    Optionally scope to a project.
    """
    filters = json.dumps([{"assignee": {"operator": "=", "values": [str(user_id)]}}])

    base = f"/api/v3/projects/{project_id}/work_packages" if project_id else "/api/v3/work_packages"

    resp = requests.get(
        f"{BASE_URL}{base}",
        auth=auth,
        params={
            "filters": filters,
            "pageSize": 100,
        },
    )
    resp.raise_for_status()

    elements = resp.json()["_embedded"]["elements"]
    for wp in elements:
        print(f"#{wp['id']} [{wp['_links']['status']['title']}] {wp['subject']}")
    return elements

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--user",
        type=int,
        help="User ID",
    )

    parser.add_argument(
        "--project",
        type=int,
        help="Project ID. If omitted, return for all projects",
    )
    
    args = parser.parse_args()

    get_my_work_packages(user_id=args.user, project_id=args.project)

if __name__ == "__main__":
    main()