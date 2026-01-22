import os
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


# Third-party libraries
import requests
from dotenv import load_dotenv

load_dotenv()

# Fetch data from Backlog REST API


@dataclass(frozen=True)
class BacklogApi:
    key = os.environ.get("backlog_api", "")
    subdomain = os.environ.get("subdomain")
    base_url = f"https://{subdomain}.backlog.com/api/v2"
    recent_activities: str = f"{base_url}/space/activities"
    issues: str = f"{base_url}/issues"


def get_backlog_activities() -> list[dict[str, Any]]:
    endpoints = BacklogApi()
    with requests.Session() as session:
        url_parameters: dict[str, str | int] = {
            "apiKey": endpoints.key,
            "count": 10,  # default 20
            # "minId": minimum ID,
        }
        response = session.get(
            url=endpoints.recent_activities, params=url_parameters, verify=False
        )
        if response.status_code != 200:
            raise ValueError(
                f"wrong response: {response.status_code=}\n{response.text=}"
            )
        return response.json()


def export_data(data: list[dict[str, Any]]) -> None:
    with Path("backlog_data.json").open(encoding="utf-8", mode="w") as f:
        json.dump(data, f, ensure_ascii=False)


def main():
    recent_activities = get_backlog_activities()
    export_data(recent_activities)


if __name__ == "__main__":
    main()
