# Ingesting Nulab Backlog Data Into Snowflake Tables: Part II

This tutorial has four parts in total:

- [Part One][first-part]
- [Part Two][second-part]
- [Part Three][third-part]
- [Part Four][fourth-part]

We will continue from where we left off in [the part one][first-part] of this tutorial.

What we are building is a Snowflake Stored Procedure that fetches data from Backlog and records it into a Snowflake table.

## Backlog

To backup data, we fist need to get data from Backlog. In this tutorial we are going to use Backlog REST API to get data.

### Authentication and Permission

Backlog API supports [two types of authentication](https://developer.nulab.com/docs/backlog/auth/): API key and OAuth 2.0 (access token). We will be using API key because authentication with it is much simpler.

To generate API key follow below steps:

1. Login to your Backlog user account
1. Click on your profile icon in the top right corner of the global navigation bar and select "Personal settings".
1. In the menu on the left side, select the "API" tab.
1. Enter a memo for the API key to help you remember its purpose or the application using it.
1. Click the "Submit" button to generate the new key.

### Backlog REST API

Using [Backlog API](https://developer.nulab.com/docs/backlog/), we can get various data such as recent activities, issues, wikis and more.

Note: Since we are going to back up Backlog data to Snowflake, we will be making `GET` requests only.

Url path format:

```txt
https://{subdomain}.backlog.com/api/v2/{recourse_path}?apiKey=abcdefghijklmn
```

Example url:

```txt
https://my_company.backlog.com/api/v2/space/activities?apiKey=abcdefghijklmn
```

I found below API endpoints useful:

- [recent updates for all projects](https://developer.nulab.com/docs/backlog/api/2/get-recent-updates/)
- [recent activities for specific projects](https://developer.nulab.com/docs/backlog/api/2/get-project-recent-updates/)
- [issues](https://developer.nulab.com/docs/backlog/api/2/get-issue-list/) (has `createdSince` and `updatedSince` parameters)
- [document list](https://developer.nulab.com/docs/backlog/api/2/get-document-list/)
- [wiki list](https://developer.nulab.com/docs/backlog/api/2/get-wiki-page-list/)

Before moving onto the Snowflake, we can write a python script to check and play around with Backlog API.

We will use [Recent Updates](https://developer.nulab.com/docs/backlog/api/2/get-recent-updates/) endpoint. Check out the specification page for available parameters and their default values.

`code_sample_1.py`

```python
import os
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


# Third-party libraries
import requests
from dotenv import load_dotenv

load_dotenv()


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
        response = session.get(url=endpoints.recent_activities, params=url_parameters, verify=False)
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
```

This code writes the fetched data in `backlog_data.json` file.

To run above code, you need to install `requests` and `python-dotenv` libraries.

One activity contains too much data, some of them may not be necessary or useful to be backed up.

Sample response:

```json
[
    {
        "id": 3153,
        "project": {
            "id": 92,
            "projectKey": "SUB",
            "name": "Subtasking",
            "chartEnabled": true,
            "useResolvedForChart": true,
            "subtaskingEnabled": true,
            "projectLeaderCanEditProjectLeader": false,
            "useWiki": true,
            "useFileSharing": true,
            "useWikiTreeView": true,
            "useSubversion": true,
            "useGit": true,
            "useOriginalImageSizeAtWiki": false,
            "textFormattingRule": "backlog",
            "archived": false,
            "displayOrder": 3,
            "useDevAttributes": true
        },
        "type": 2,
        "content": {
            "id": 4809,
            "key_id": 121,
            "summary": "Comment",
            "description": "",
            "comment": {
                "id": 7237,
                "content": ""
            },
            "changes": [
                {
                    "field": "milestone",
                    "new_value": "R2014-07-23",
                    "old_value": "",
                    "type": "standard"
                },
                {
                    "field": "status",
                    "new_value": "4",
                    "old_value": "1",
                    "type": "standard"
                }
            ]
        },
        "notifications": [],
        "createdUser": {
            "id": 1,
            "userId": "admin",
            "name": "admin",
            "roleType": 1,
            "lang": "ja",
            "nulabAccount": {
                "nulabId": "Prm9ZD9DQD5snNWcSYSwZiQoA9WFBUEa2ySznrSnSQRhdC2X8G",
                "name": "admin",
                "uniqueId": "admin"
            },
            "mailAddress": "eguchi@nulab.example",
            "lastLoginTime": "2022-09-01T06:35:39Z"
        },
        "created": "2013-12-27T07:50:44Z"
    },
    // ...
]
```

We may be interested in only subset of the response data. Flattening certain fields, such as `createdUser` would also be better. In addition, `type` id is not clear enough, it would be easier to understand what it means if we add "activity type".

> There are 26 defined activity types. Check out the Backlog API overview page for details.

`code_sample_2.py`

```python
import os
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any


# Third-party libraries
import requests
from dotenv import load_dotenv

load_dotenv()


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
```

Now we know what kind of data we can get from Backlog. We also simplified the data we can get. Next, let's move on to Stored Procedures.

## Snowflake Stored Procedures

Snowflake stored procedures are similar to functions in many programming languages. Stored procedure consists of two parts: **wrapper** (written in SQL) and **handler** (the main logic, can be written in  in Python, JavaScript, [Snowflake Scripting](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-snowflake-scripting) (SQL), Java and Scala).

Syntax:

```txt
SQL Boilerplate wrapper
$$
    handler (logic written in one of the supported languages)
$$
```

Based on which language you use for your handler, (boilerplate) wrapper code might differ slightly.

**Precautions:**

- By default stored procedures are not atomic; if one statement in a stored procedure fails, the other statements (the ones executed prior to failed statement) are not necessarily rolled back. We are not going to use it, but if you want it is possible to [use stored procedures with transactions](https://docs.snowflake.com/en/sql-reference/transactions#stored-procedures-and-transactions) to create an atomic behavior.

- Stored procedures can dynamically create a SQL statement and execute it. You should minimize the risk of SQL injection attacks by [binding parameters](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-javascript.html#label-stored-procedures-binding-variables) instead of concatenating text.

JavaScript Stored procedure example:

```sql
CREATE OR REPLACE PROCEDURE demo_procedure(table_name VARCHAR)
  RETURNS VARCHAR
  LANGUAGE JAVASCRIPT
  AS
  $$
    // in JavaScript handler, input arguments must be uppercase
    let my_sql_command = `Alter table ${TABLE_NAME} ...`;
    // in JavaScript handler, snowflake object is available globally
    let statement = snowflake.createStatement( {sqlText: my_sql_command} );
    let result_set = statement.execute();
    return "Table has been altered";
  $$
  ;
```

JavaScript stored procedure doesn't have to include functions. No need to specify entry point either.

Python Stored procedure Example:

`code_sample_3.sql`

```python
CREATE OR REPLACE PROCEDURE table_exists(table_name VARCHAR)
RETURNS BOOLEAN NOT NULL
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core')
HANDLER = 'main' -- entry point to our handler
AS
$$
def some_function():
    pass

def main(snowflake_session, table_name: str) -> bool:
    session = snowflake_session

    some_function()

    return session.catalog.tableExists(table_name)
$$;
```

In python stored procedures, entry point function name (`HANDLER`), python version (`RUNTIME_VERSION`),  and packages (`PACKAGES`) should be specified in the wrapper part.

When you call python stored procedure, Snowflake automatically creates a Session object and passes it to the stored procedure. The entry point function should accept session object as a first argument.

Calling stored procedures:

```sql
call table_exists('my_table') -- use single quotes
```

Now, we can move on to creating stored procedures. We will continue with it in [the part three][third-part] of these series.

[first-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-i.html
[second-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-ii.html
[third-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-iii.html
[fourth-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-iv.html
