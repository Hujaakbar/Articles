import os
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


# Third-party libraries
import requests
from dotenv import load_dotenv

load_dotenv()

# Fetch data from Backlog REST API
# Flatten the response, and store it in dataclass


@dataclass(frozen=True)
class BacklogApi:
    key = os.environ.get("backlog_api", "")
    subdomain = os.environ.get("subdomain")
    base_url = f"https://{subdomain}.backlog.com/api/v2"
    recent_activities: str = f"{base_url}/space/activities"
    issues: str = f"{base_url}/issues"


@dataclass(frozen=True, kw_only=True)
class BacklogActivity:
    activity_id: int
    activity_type: str
    activity_type_id: int
    project_id: int
    project_key: str
    project_name: str
    content: dict[str, Any]
    creator_id: int
    creator_name: str
    creator_email_address: str | None
    creator_nulab_account_id: str
    creator_nulab_unique_id: str
    created_at: str


def parse_activity_type(*, activity_type_id: int) -> str:
    activity = {
        1: "Issue Created",
        2: "Issue Updated",
        3: "Issue Commented",
        4: "Issue Deleted",
        5: "Wiki Created",
        6: "Wiki Updated",
        7: "Wiki Deleted",
        8: "File Added",
        9: "File Updated",
        10: "File Deleted",
        11: "SVN Committed",
        12: "Git Pushed",
        13: "Git Repository Created",
        14: "Issue Multi Updated",
        15: "Project User Added",
        16: "Project User Deleted",
        17: "Comment Notification Added",
        18: "Pull Request Added",
        19: "Pull Request Updated",
        20: "Comment Added on Pull Request",
        21: "Pull Request Deleted",
        22: "Milestone Created",
        23: "Milestone Updated",
        24: "Milestone Deleted",
        25: "Project Group Added",
        26: "Project Group Deleted",
    }
    return activity.get(activity_type_id, "Unknown activity_type_id")


def get_backlog_activities() -> list[BacklogActivity]:
    endpoints = BacklogApi()
    with requests.Session() as session:
        url = endpoints.recent_activities
        url_parameters: dict[str, str | int] = {
            "apiKey": endpoints.key,
            "count": 2,
            # "minId": last_activity_id,
        }

        response = session.get(url=url, params=url_parameters, verify=False)
        if response.status_code != 200:
            raise ValueError(
                f"wrong response: {response.status_code=}\n{response.text=}"
            )

        backlog_activities: list[BacklogActivity] = []
        for data in response.json():
            activity_creator = data.get("createdUser")
            backlog_activity = BacklogActivity(
                activity_id=data["id"],
                activity_type=parse_activity_type(activity_type_id=data["type"]),
                activity_type_id=data["type"],
                project_id=data["project"]["id"],
                project_key=data["project"]["projectKey"],
                project_name=data["project"]["name"],
                content=data["content"],
                created_at=data["created"],
                creator_id=activity_creator["id"],
                creator_name=activity_creator["name"],
                creator_email_address=activity_creator["mailAddress"],
                creator_nulab_account_id=activity_creator["nulabAccount"]["nulabId"],
                creator_nulab_unique_id=activity_creator["nulabAccount"]["uniqueId"],
            )

            backlog_activities.append(backlog_activity)
        return backlog_activities


def export_data(data: list[BacklogActivity]) -> None:
    with Path("backlog_data_enhanced.json").open(encoding="utf-8", mode="w") as f:
        json.dump([asdict(d) for d in data], f, ensure_ascii=False)


def main():
    recent_activities = get_backlog_activities()
    export_data(recent_activities)


if __name__ == "__main__":
    main()
