CREATE OR REPLACE SECRET backlog_api_key
  TYPE = GENERIC_STRING
  SECRET_STRING = 'backlog_api_key_xyz';

GRANT READ ON SECRET backlog_api_key TO ROLE <my_role>;
-- -------------------------------------------
USE ROLE SYSADMIN;
CREATE NETWORK RULE external_access_network_rule_for_backlog
TYPE = HOST_PORT
MODE = EGRESS
VALUE_LIST = ('*.backlog.com:0')
COMMENT = 'Network rule for Backlog REST API endpoint';
-- -------------------------------------------
USE ROLE ACCOUNTADMIN;
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION backlog_api_access_integration
ALLOWED_NETWORK_RULES = (external_access_network_rule_for_backlog)
ALLOWED_AUTHENTICATION_SECRETS = (backlog_api_key)
ENABLED = true;

GRANT USAGE ON INTEGRATION backlog_api_access_integration TO ROLE <my_role>;

-------------------------------------------
CREATE OR REPLACE PROCEDURE backup_backlog_data(table_name VARCHAR)
RETURNS STRING NOT NULL
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core', 'requests')
HANDLER = 'main' -- entry point to our handler
EXTERNAL_ACCESS_INTEGRATIONS= (backlog_api_access_integration)
SECRETS = ('backlog_key'= backlog_api_key)
AS
$$
from dataclasses import dataclass, asdict
from types import NoneType, UnionType
from typing import (
    Annotated,
    Any,
    Literal,
    NoReturn,
    TypedDict,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import requests
from _snowflake import get_generic_secret_string
from snowflake.snowpark.types import StructType
import snowflake.snowpark.functions as f

# insert data into table


@dataclass(frozen=True, kw_only=True)
class BacklogActivity:
    activity_id: int
    activity_type_id: int
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


# ----------- fetch backlog data --------------

@dataclass(frozen=True)
class BacklogApi:
    key = get_generic_secret_string("backlog_key")
    subdomain = "subdomain"
    base_url = f"https://my-org.backlog.com/api/v2"
    recent_activities: str = f"{base_url}/space/activities"
    issues: str = f"{base_url}/issues"


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


def fetch_backlog_data(last_activity_id: int) -> list[BacklogActivity]:
    endpoints = BacklogApi()
    with requests.Session() as session:
        url_parameters: dict[str, str | int] = {
            "apiKey": endpoints.key,
            "count": 100,
            "minId": last_activity_id,
            "order": "desc"
        }

        response = session.get(
            url=endpoints.recent_activities, params=url_parameters, verify=True
        )
        if response.status_code != 200:
            raise ValueError(
                f"wrong response: {response.status_code=}\n{response.text=}"
            )

        backlog_data: list[BacklogActivity] = []
        for data in response.json():
            activity_creator = data.get("createdUser")
            backlog_activity = BacklogActivity(
                activity_id=data["id"],
                activity_type_id=data["type"],
                activity_type=parse_activity_type(activity_type_id=data["type"]),
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

            backlog_data.append(backlog_activity)
        return backlog_data


# ---- Create table definition from dataclass metadata -------


class ColumnDefinition(TypedDict):
    name: str
    type: str
    nullable: bool


class ClassParser:
    """
    Parses the class attributes that use type hinting and generates column definitions compatible with Snowflake Snowpark API.
    If class attribute does not use type hinting, it is omitted from generated column definitions.
    """

    def __init__(self):
        pass

    @property
    def snowflake_supported_types(self):
        return {
            "string",
            "integer",
            "float",
            "decimal",
            "double",
            "short",
            "long",
            "boolean",
            "variant",
            "timestamp",
            "timestamp_tz",
            "timestamp_ltz",
            "timestamp_ntz",
            # There are more supported types
        }

    @snowflake_supported_types.setter
    def snowflake_supported_types(self, value: Any) -> NoReturn:
        raise ValueError("Assigning value is not allowed")

    def parse_class(self, _class: object) -> dict[str, list[ColumnDefinition]]:
        """
        takes a class, not a class instance and returns a dictionary of column definition inferred from class attributes.

        class fields cannot contain more than two type hints.
        If a field contains two type hints, one of the types must be NoneType.

        To specify Snowflake specific field such as TIMESTAMP_NTZ, use Annotated type hints
        e.g.

        ```python
        class A:
            field1: Annotated[str, "timestamp_ntz"]
        ```

        """
        columns: list[ColumnDefinition] = []
        for fieldname, type_hint in get_type_hints(_class, include_extras=True).items():
            result = self._parse_type_hint(type_hint)
            datatype, nullable = result
            columns.append(
                ColumnDefinition(name=fieldname, type=datatype, nullable=nullable)
            )
        return {"fields": columns}

    def _parse_type_hint(self, type_hint: object | UnionType) -> tuple[str, bool]:
        """
        returns a tuple of (datatype, nullable): tuple[str, bool]
        """
        datatype = ""
        nullable = False

        if res := self._parse_annotated_type(type_hint):
            if res["snowflake_type"]:
                datatype = res["snowflake_type"]
                nullable = True if self._parse_union_type(res["origin_type"]) else False
                return (datatype, nullable)
            type_hint = res["origin_type"]

        # This supports generic types, Callable, Tuple, Union, Literal, Final, ClassVar,
        # Annotated, and others. Return None for unsupported types.
        # get_origin never returns Optional, instead it returns Union
        complex_type = get_origin(type_hint)
        if res := self._parse_union_type(type_hint):
            main_type, nullable = res[0], res[1]
            type_hint = main_type  # main type is any type hint except for None
            complex_type = get_origin(main_type)
        if complex_type is Literal:
            atomic_type = get_args(type_hint)[0]
            datatype = self._translate_atomic_type(atomic_type)
        if complex_type in [dict, list, TypedDict, tuple]:
            datatype = "variant"
        if not complex_type:
            datatype = self._translate_atomic_type(type_hint)
        return (datatype, nullable)

    def _parse_annotated_type(self, type_hint: Any) -> dict[str, Any] | None:
        """
        returns dict of snowflake_type:str and origin_type: Any

        returns None if given type_hint is not Annotated

        If Annotated does not contain Snowflake data types,
        it returns `{"snowflake_type": "", "original_type": origin_type}`
        """
        if get_origin(type_hint) is not Annotated:
            return

        metadata = [
            metadata.strip().lower()
            for metadata in type_hint.__metadata__
            if isinstance(metadata, str)
        ]
        snow_types = self.snowflake_supported_types.intersection(metadata)

        if len(snow_types) > 1:
            raise ValueError(
                "Annotated cannot contain more than one snowflake data type"
            )

        snowflake_type = snow_types.pop() if snow_types else ""
        origin_type = type_hint.__origin__
        return {"snowflake_type": snowflake_type, "origin_type": origin_type}

    def _parse_union_type(self, type_hint: Any) -> tuple[object, bool] | None:
        """
        returns None if given type_hint is not UnionType

        UnionType must contain only two types and one of these types must be NoneType
        """
        types = get_args(type_hint)
        nullable = True
        if get_origin(type_hint) not in [Union, UnionType] or len(types) < 2:
            return
        if len(types) > 2:
            raise ValueError("Union type cannot contain more than two types")
        if NoneType not in types:
            raise ValueError("Union type must include NoneType")
        main_type = types[0] if types[0] is not NoneType else types[1]

        return (main_type, nullable)

    def _translate_atomic_type(self, atomic_type: object) -> str:
        snowflake_type = ""
        if atomic_type is str or isinstance(atomic_type, str):
            snowflake_type = "string"
        if atomic_type is int or isinstance(atomic_type, int):
            snowflake_type = "integer"
        if atomic_type is float or isinstance(atomic_type, float):
            snowflake_type = "float"
        if atomic_type is bool or isinstance(atomic_type, bool):
            snowflake_type = "boolean"
        if not snowflake_type:
            raise RuntimeError(
                f"{atomic_type=} is not defined in this method thus can't be translated"
            )
        return snowflake_type


def create_table_definition(_class: object) -> StructType:
    parser = ClassParser()
    column_definitions = parser.parse_class(_class)
    table_definition: StructType = StructType.from_json(column_definitions)
    return table_definition


def create_or_replace_table(session, table_name: str, table_definition: StructType):
    dataframe = session.create_dataframe([], schema=table_definition)
    if session.catalog.tableExists(table_name):
        dataframe.write.mode("overwrite").save_as_table(table_name)
        return
    # creates table if the table does not already exists.
    # otherwise, simple ignores this operation
    dataframe.write.mode("ignore").save_as_table(table_name)


def create_table(session, table_name: str, table_definition: StructType):
    dataframe = session.create_dataframe([], schema=table_definition)
    # Throws an exception if the table already exists.
    dataframe.write.mode("errorifexists").save_as_table(table_name)


def insert_data(
    session, table_name: str, table_definition: StructType, data: list[list[Any]]
):
    dataframe = session.create_dataframe(data, schema=table_definition)
    dataframe.write.mode("append").save_as_table(table_name)

def get_last_recorded_value(session, table_name: str, column_name: str) -> int | None:
    column_name = column_name.strip().upper()
    dframe_backlog_data = session.table(table_name)
    if column_name not in dframe_backlog_data.columns:
        raise ValueError(
            f"{column_name} is not defined in the given table {table_name}"
        )
    column_alias = f"LAST_{column_name}"
    result: list[Any] = dframe_backlog_data.agg(
        f.max(column_name).alias(column_alias)
    ).collect()
    # returns none if there are not records
    return result[0][column_alias]


def main(snowflake_session, table_name: str):
    session = snowflake_session
    table_definition = create_table_definition(BacklogActivity)

    if not session.catalog.tableExists(table_name):
        create_table(session, table_name, table_definition)

    last_activity_id = get_last_recorded_value(session, table_name, "activity_id") or 0
    count = 0
    api_requests = 0
    while backlog_data := fetch_backlog_data(last_activity_id):
        values = [list(asdict(data).values()) for data in backlog_data]
        insert_data(session, table_name, table_definition, values)
        last_activity_id = backlog_data[0].activity_id
        count += len(values)
        api_requests += 1
    return f"{count} rows of data have been inserted into {table_name} in {api_requests} api_requests"
$$;

-- call backup_backlog_data('backlog_data');

-- select * from backlog_data;
-------------------------------------
CREATE TASK backup_backlog_data
  SCHEDULE='60 MINUTES'
  SERVERLESS_TASK_MAX_STATEMENT_SIZE='LARGE'
  SUSPEND_TASK_AFTER_NUM_FAILURES = 1
  AS 
    call backup_backlog_data('backlog_data');

ALTER TASK backup_backlog_data resume;