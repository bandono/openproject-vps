#!/usr/bin/env python3

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

def get_my_mentions() -> list[dict]:
    """
    Get all notifications where the authenticated user was mentioned.
    """
    resp = requests.get(
        f"{BASE_URL}/api/v3/notifications",
        auth=auth,
        params={
            "filters": json.dumps([
                {"reason": {"operator": "=", "values": ["mentioned"]}}
            ]),
            "pageSize": 100,
        },
    )
    resp.raise_for_status()

    elements = resp.json()["_embedded"]["elements"]
    for n in elements:
        wp = n["_links"]["resource"]
        print(f"Mentioned in: {wp['title']} — {wp['href']}")
    return elements

def main():
    get_my_mentions()

if __name__ == "__main__":
    main()