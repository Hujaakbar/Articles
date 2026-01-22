from dataclasses import dataclass, asdict
from typing import Annotated, Any

# create sample data


@dataclass(frozen=True, kw_only=True)
class BacklogActivity:
    activity_id: int
    type_id: int
    activity_type: str
    project_id: int
    project_key: str
    project_name: str
    content: dict[str, Any]
    creator_id: int
    creator_name: str
    creator_email_address: str | None
    creator_nulab_account_id: str
    creator_nulab_unique_id: str
    created_at: Annotated[str, "timestamp_ntz"]


def create_sample_data() -> list[BacklogActivity]:
    data1 = BacklogActivity(
        activity_id=630,
        type_id=2,
        activity_type="Issue Updated",
        project_id=61,
        project_key="MY_IT_006",
        project_name="XYZ",
        content={
            "id": 200,
            "key_id": 36,
            "summary": "loreum",
            "description": "lorem ipsum",
            "comment": {"id": 76, "content": "Great"},
            "changes": [
                {
                    "field": "description",
                    "field_text": "Description",
                    "new_value": "description version 2",
                    "old_value": "description version 1",
                    "type": "standard",
                }
            ],
            "attachments": [],
            "shared_files": [],
            "external_file_links": [],
        },
        created_at="2026-01-18T06:22:30Z",
        creator_id=80,
        creator_name="John Doe",
        creator_email_address=None,
        creator_nulab_account_id="xyzt",
        creator_nulab_unique_id="JohnDoe007",
    )
    data2 = BacklogActivity(
        activity_id=631,  # <<--- different activity_id
        type_id=2,
        activity_type="Issue Updated",
        project_id=11,
        project_key="MY_IT_006",
        project_name="XYZ",
        content={
            "id": 200,
            "key_id": 36,
            "summary": "loreum",
            "description": "lorem ipsum",
            "comment": {"id": 76, "content": "Great"},
            "changes": [
                {
                    "field": "description",
                    "field_text": "Description",
                    "new_value": "description version 2",
                    "old_value": "description version 1",
                    "type": "standard",
                }
            ],
            "attachments": [],
            "shared_files": [],
            "external_file_links": [],
        },
        created_at="2026-01-19T06:22:30Z",
        creator_id=80,
        creator_name="John Doe",
        creator_email_address=None,
        creator_nulab_account_id="xyzt",
        creator_nulab_unique_id="JohnDoe007",
    )
    return [data1, data2]


def main():
    sample_data = create_sample_data()
    values = [list(asdict(data).values()) for data in sample_data]
    print(values)


if __name__ == "__main__":
    main()
