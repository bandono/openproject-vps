#!/usr/bin/env python3

import argparse
import json
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

CONFIG_PATH = Path(__file__).parent.parent / ".config" / "client-settings.json"
LANE_PATH = Path(__file__).parent / "board-settings.json"

config = json.loads(CONFIG_PATH.read_text())
LANES = json.loads(LANE_PATH.read_text())

BASE_URL = config["base_url"]
API_KEY = config["api_key"]

auth = HTTPBasicAuth("apikey", API_KEY)

def get_current_lane(wp_id: int) -> tuple[str, int] | None:
    """
    Returns:
        ("Sprint Backlog", 41)

    or None if not found.
    """
    wp_id = str(wp_id)

    for lane_name, cfg in LANES.items():
        query_id = cfg["query_id"]

        try:
            resp = requests.get(
                f"{BASE_URL}/api/v3/queries/{query_id}/order",
                auth=auth,
            )
            resp.raise_for_status()
            data = resp.json()

            if wp_id in data:
                return lane_name, query_id

        except Exception as e:
            print(f"Failed checking lane '{lane_name}': {e}")

    return None


def update_status(wp_id: int, status_id: int) -> dict:
    wp = requests.get(
        f"{BASE_URL}/api/v3/work_packages/{wp_id}",
        auth=auth,
    )
    wp.raise_for_status()

    wp = wp.json()

    resp = requests.patch(
        f"{BASE_URL}/api/v3/work_packages/{wp_id}",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json={
            "lockVersion": wp["lockVersion"],
            "_links": {
                "status": {
                    "href": f"/api/v3/statuses/{status_id}"
                }
            },
        },
    )

    resp.raise_for_status()
    return resp.json()

def move_wp_to_lane(
    wp_id: int,
    to_lane: str,
    position: int = 0,
    status_id: int | None = None,
) -> None:
    """
    Move a work package to another lane.

    If status_id is omitted, the lane's configured
    default status_id will be applied.
    """

    if to_lane not in LANES:
        raise ValueError(f"Unknown lane: {to_lane}")

    current = get_current_lane(wp_id)

    if current:
        current_name, current_query_id = current

        if current_name == to_lane:
            print(f"WP #{wp_id} already in '{to_lane}'")
        else:
            requests.patch(
                f"{BASE_URL}/api/v3/queries/{current_query_id}/order",
                auth=auth,
                headers={"Content-Type": "application/json"},
                json={"delta": {str(wp_id): -1}},
            ).raise_for_status()

            print(f"Removed WP #{wp_id} from '{current_name}'")

            requests.patch(
                f"{BASE_URL}/api/v3/queries/{LANES[to_lane]['query_id']}/order",
                auth=auth,
                headers={"Content-Type": "application/json"},
                json={"delta": {str(wp_id): position}},
            ).raise_for_status()

            print(f"Moved WP #{wp_id} to '{to_lane}'")

    else:
        requests.patch(
            f"{BASE_URL}/api/v3/queries/{LANES[to_lane]['query_id']}/order",
            auth=auth,
            headers={"Content-Type": "application/json"},
            json={"delta": {str(wp_id): position}},
        ).raise_for_status()

        print(f"Added WP #{wp_id} to '{to_lane}'")

    if status_id is None:
        status_id = LANES[to_lane].get("status_id")

    if status_id:
        update_status(wp_id, status_id)
        print(f"Updated WP #{wp_id} status to {status_id}")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "wp_id",
        type=int,
        help="Work package ID",
    )

    parser.add_argument(
        "--lane",
        required=True,
        choices=sorted(LANES.keys()),
        help="Target lane",
    )

    parser.add_argument(
        "--position",
        type=int,
        default=0,
        help="Board position (default: 0)",
    )

    parser.add_argument(
        "--status",
        type=int,
        help="Override status ID. If omitted, lane default is used.",
    )

    args = parser.parse_args()

    move_wp_to_lane(
        wp_id=args.wp_id,
        to_lane=args.lane,
        position=args.position,
        status_id=args.status,
    )


if __name__ == "__main__":
    main()