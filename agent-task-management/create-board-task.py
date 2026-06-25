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

TASK_TYPE_ID = 1 # Current setting of type Task (other are Epic, User Story, Bug, etc.)


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


def create_task(
    project_id : int,
    subject: str,
    description: str,
    parent_id: int,
    assignee_id: int | None = None,
):
    url = f"{BASE_URL}/api/v3/projects/{project_id}/work_packages"

    links = {
        "type": {
            "href": f"/api/v3/types/{TASK_TYPE_ID}"
        },
        "parent": {
            "href": f"/api/v3/work_packages/{parent_id}"
        }
    }

    if assignee_id:
        links["assignee"] = {
            "href": f"/api/v3/users/{assignee_id}"
        }

    payload = {
        "subject": subject,
        "description": {
            "raw": description
        },
        "_links": links
    }

    resp = requests.post(
        url,
        auth=auth,
        headers={"Content-Type": "application/json"},
        json=payload,
    )

    resp.raise_for_status()
    return resp.json()


def add_wp_to_lane(
    wp_id: int,
    lane_name: str,
    position: int = 0,
    retries: int = 3,
):
    query_id = LANES[lane_name]['query_id']

    for attempt in range(retries):
        try:
            resp = requests.patch(
                f"{BASE_URL}/api/v3/queries/{query_id}/order",
                auth=auth,
                headers={"Content-Type": "application/json"},
                json={
                    "delta": {
                        str(wp_id): position
                    }
                },
            )

            resp.raise_for_status()

            print(
                f"WP #{wp_id} added to "
                f"'{lane_name}' "
                f"(query={query_id}) "
                f"position={position}"
            )
            return

        except requests.HTTPError as ex:
            if attempt == retries - 1:
                raise

            print(
                f"Board update failed "
                f"(attempt {attempt+1}/{retries}), retrying..."
            )

            time.sleep(1)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
    "--project",
    required=True,
    type=int,
    help="OpenProject project id"
    )

    parser.add_argument(
        "--parent",
        required=True,
        type=int,
        help="Parent story WP ID"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Markdown task file"
    )

    parser.add_argument(
        "--lane",
        default="Sprint Backlog",
        help="Board lane name"
    )

    parser.add_argument(
        "--position",
        type=int,
        default=0,
        help="Board position"
    )

    parser.add_argument(
        "--assignee",
        type=int,
        help="OpenProject user id"
    )

    args = parser.parse_args()

    subject, description = parse_markdown(
        Path(args.file)
    )

    result = create_task(
        project_id=args.project,
        subject=subject,
        description=description,
        parent_id=args.parent,
        assignee_id=args.assignee,
    )

    wp_id = result["id"]

    print(
        f"Created WP #{wp_id}: "
        f"{result['subject']}"
    )

    add_wp_to_lane(
        wp_id=wp_id,
        lane_name=args.lane,
        position=args.position,
    )


if __name__ == "__main__":
    main()