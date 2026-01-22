# Ingesting Nulab Backlog Data Into Snowflake Tables: Part III

This tutorial has four parts in total:

- [Part One][first-part]
- [Part Two][second-part]
- [Part Three][third-part]
- [Part Four][fourth-part]

We will continue from where we left off in [the part two][second-part] of this tutorial.

Before diving into creating Snowflake objects, let's see what the final result looks like once again:

1. Snowflake Task calls Stored Procedure every few hours
1. Stored Procedure fetches data from Backlog API
1. Stored Procedure records the fetched data into Snowflake table

In this tutorial we will create Python Stored Procedure. Instead of dumping all the code at once, I will incrementally build up our solution.

## Creating Python Stored Procedure

Ultimately our stored procedure will be fetching data from backlog and recording it onto given table. If table does not exist, it should create the table. First let's build the part of our stored procedure that checks if table exists or not.

`code_sample_4.sql`

```python
CREATE OR REPLACE PROCEDURE backup_backlog_data(table_name VARCHAR)
RETURNS STRING NOT NULL
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core')
HANDLER = 'main' -- entry point to our handler
AS
$$
def main(snowflake_session, table_name: str) -> str:
    session = snowflake_session
    if session.catalog.tableExists(table_name):
        return f"table {table_name} already exists"
    return f"table {table_name} does not exist"
$$;

call backup_backlog_data('backlog_data');
```

In above code, since we are not providing database and schema names, stored procedure will be created in the current database and schema. When checking the existence of the table too, the stored procedure will be checking against current database and schema. If you want, you can provide database and schema names.

Unsurprisingly, the table does not exist yet. As a next step, our stored procedure should create a table.

`code_sample_5.py`

```python
CREATE OR REPLACE PROCEDURE backup_backlog_data(table_name VARCHAR)
RETURNS STRING NOT NULL
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core')
HANDLER = 'main' -- entry point to our handler
AS
$$
from snowflake.snowpark.types import StructType


def create_table_definition() -> StructType:
    json_data = {
        "fields": [
            {"name": "col_1", "type": "string", "nullable": True},
            {"name": "col_2", "type": "string", "nullable": False},
            {"name": "col_3", "type": "variant", "nullable": True},
        ]
    }
    table_definition: StructType = StructType.from_json(json_data)
    return table_definition


def main(snowflake_session, table_name: str) -> str:
    session = snowflake_session

    if session.catalog.tableExists(table_name):
        return f"table {table_name} already exists"

    table_definition = create_table_definition()
    dataframe = session.create_dataframe([], schema=table_definition)
    dataframe.write.mode("ignore").save_as_table(table_name)
    return f"table {table_name} has been created"
$$;

call backup_backlog_data('backlog_data');

select * from backlog_data;
```

All of a sudden there are many new stuff in our code. Let me go over them one by one.

[StructType](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.types.StructType#snowflake.snowpark.types.StructType) instance represents a table schema (DDL). StructType is a class, when we initialize it, it returns its instance whose fields represent columns via [StructField](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.types.StructField#snowflake.snowpark.types.StructField)s. Subjectively, the easiest way to initialize `StructType` is by using its `from_json` method.

Snowflake extensively uses dataframes, if you know them, that's great. If you don't know them, don't sweat. You can simply think of dataframe as an object representing a table.

[session.create_dataframe](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.Session.create_dataframe) method creates a dataframe in the memory with given column names, their datatype and null constraints. In the next line we are saving the dataframe in the database as a table. (It is possible to convert dataframe into csv and save it into Snowflake stages as well.)

> You may be wondering where I got the `mode("ignore")` part. The [docs page](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.DataFrame.write) gives almost no information on available options.
>
> Snowflake documentation is poor. To get more detailed information on any of the Snowflake concepts discussed on this post and beyond, click the "\[source]" link on SIGNATURE section of the documentation page. The link takes you to a GitHub source page.
>
> ![alt text](https://i.imgur.com/21Uv34I.png)

`mode` can take any of the below values.

"append"
: Append data of this DataFrame to the existing table. Creates a table if it does not exist.

"overwrite"
: Overwrite the existing table by dropping old table.

"truncate"
: Overwrite the existing table by truncating old table.

"errorifexists"
: Throw an exception if the table already exists.

"ignore"
: Ignore this operation if the table already exists.

Default value is "errorifexists".

> Because `ignore` mode creates table only if it doesn't already exist, we don't need to check the existence of the table in the if statement of previous example. I decided to keep it for readability.

### Converting Python Dataclass to Snowflake StructType

We learnt how to create tables using dataframes. But we haven't created the table we need yet. We need a table with columns like `activity_id`, `activity_type`,`activity_type_id` etc, basically the same as the fields of our `BacklogActivity` dataclass.

As we saw in the previous example, we define the table structure using `StructType`. `StructType` needs information on columns.

```python
json_data = {
        "fields": [
            {"name": "col_1", "type": "string", "nullable": True},
            {"name": "col_2", "type": "string", "nullable": False},
            {"name": "col_3", "type": "variant", "nullable": True},
        ]
    }
table_definition: StructType = StructType.from_json(json_data)
```

When we initialize StructType, we should specify the column name, datatype and whether it is nullable or not. Exact same data is defined in our `BacklogActivity` dataclass, though in a slightly different format.

```python
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
    creator_email_address: str | None # nullable
    creator_nulab_account_id: str
    creator_nulab_unique_id: str
    created_at: Annotated[str, "timestamp_ntz"]
```

Our next goal is to extract necessary data (field names, datatypes and nullability) from `BacklogActivity` dataclass in JSON format and use it to create StructType (table definition).

`code_sample_6.py`

```python
from dataclasses import dataclass
from pprint import pprint
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

# Create table definition from dataclass metadata


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
        takes a class, not a class instance, and returns a dictionary of column definitions inferred from class attributes.

        class fields cannot contain more than two types.
        If a field contains two types, one of the types must be NoneType.

        To specify Snowflake specific field such as TIMESTAMP_NTZ, use Annotated type hints
        e.g.

        \```python
        class A:
            field1: Annotated[str, "timestamp_ntz"]
        \```
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
            type_hint = main_type # main type is any type hint except for None
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

        UnionType must contain only two types and one of these types must be NoneType.

        Raises exception if UnionType does not include NoneType.
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


def create_column_definitions():
    parser = ClassParser()
    pprint(parser.parse_class(BacklogActivity), sort_dicts=False)


if __name__ == "__main__":
    create_column_definitions()
```

Above code outputs this:

```python
{'fields': [{'name': 'activity_id', 'type': 'integer', 'nullable': False},
            {'name': 'type_id', 'type': 'integer', 'nullable': False},
            {'name': 'activity_type', 'type': 'string', 'nullable': False},
            {'name': 'project_id', 'type': 'integer', 'nullable': False},
            {'name': 'project_key', 'type': 'string', 'nullable': False},
            {'name': 'project_name', 'type': 'string', 'nullable': False},
            {'name': 'content', 'type': 'variant', 'nullable': False},
            {'name': 'creator_id', 'type': 'integer', 'nullable': False},
            {'name': 'creator_name', 'type': 'string', 'nullable': False},
            {'name': 'creator_email_address', 'type': 'string', 'nullable': True},
            {'name': 'creator_nulab_account_id', 'type': 'string', 'nullable': False},
            {'name': 'creator_nulab_unique_id', 'type': 'string', 'nullable': False},
            {'name': 'created_at', 'type': 'timestamp_ntz', 'nullable': False}]}
```

Types that Snowflake [StructField](https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.types.StructField#snowflake.snowpark.types.StructField) accepts are the following:

- string
- binary
- boolean
- decimal
- float
- double
- byte
- short
- integer
- long
- date
- null
- timestamp
- timestamp_ltz
- timestamp_ntz
- array
- map
- [variant](https://docs.snowflake.com/en/sql-reference/data-types-semistructured) (for objects, dictionaries and lists)
- *some more*

> You can check these and other accepted data-types on the GitHub source page of `StructField`.

Now let's put it together, and create a proper table using dataclass metadata.

If you haven't dropped previously created table, you should drop it.

```sql
drop table backlog_data;
```

`code_sample_7.sql`

```python
CREATE OR REPLACE PROCEDURE backup_backlog_data(table_name VARCHAR)
RETURNS STRING NOT NULL
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core')
HANDLER = 'main' -- entry point to our handler
AS
$$
# Create table from dataclass metadata
from dataclasses import dataclass
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

from snowflake.snowpark.types import StructType


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

        \```python
        class A:
            field1: Annotated[str, "timestamp_ntz"]
        \```

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

        UnionType must contain only two types and one of these types must be NoneType.

        Raises exception if UnionType does not include NoneType.
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


def main(snowflake_session, table_name: str):
    session = snowflake_session
    table_definition = create_table_definition(BacklogActivity)

    if not session.catalog.tableExists(table_name):
        create_table(session, table_name, table_definition)

    return f"table {table_name} has been created"

$$;

call backup_backlog_data('backlog_data');

select * from backlog_data;
```

## Inserting Data

The table has been created. Now let's learn how to insert data into our table. Snowflake procedures cannot access the internet by default. To enable internet access we need to create external access integration. But before that let's just create a `insert_into` function and test it with sample data.

Preparing sample data.

`code_sample_8.py`

```python
from dataclasses import dataclass, asdict
from typing import Annotated, Any

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
```

output:

```json
[
    [630, 2, 'Issue Updated', 61, 'MY_IT_006', 'XYZ', {'id': 200, 'key_id': 36, 'summary': 'loreum', 'description': 'lorem ipsum', 'comment': {'id': 76, 'content': 'Great'}, 'changes': [{'field': 'description', 'field_text': 'Description', 'new_value': 'description version 2', 'old_value': 'description version 1', 'type': 'standard'}], 'attachments': [], 'shared_files': [], 'external_file_links': []}, 80, 'John Doe', None, 'xyzt', 'JohnDoe007', '2026-01-18T06:22:30Z'],
    [631, 2, 'Issue Updated', 11, 'MY_IT_006', 'XYZ', {'id': 200, 'key_id': 36, 'summary': 'loreum', 'description': 'lorem ipsum', 'comment': {'id': 76, 'content': 'Great'}, 'changes': [{'field': 'description', 'field_text': 'Description', 'new_value': 'description version 2', 'old_value': 'description version 1', 'type': 'standard'}], 'attachments': [], 'shared_files': [], 'external_file_links': []}, 80, 'John Doe', None, 'xyzt', 'JohnDoe007', '2026-01-19T06:22:30Z']
]
```

Insert sample data into our table:

`code_sample_9.sql`

```python
CREATE OR REPLACE PROCEDURE backup_backlog_data(table_name VARCHAR)
RETURNS STRING NOT NULL
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core')
HANDLER = 'main' -- entry point to our handler
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

from snowflake.snowpark.types import StructType

# insert data into table

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


# Create table definition from dataclass metadata


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


def main(snowflake_session, table_name: str):
    session = snowflake_session
    table_definition = create_table_definition(BacklogActivity)

    if not session.catalog.tableExists(table_name):
        create_table(session, table_name, table_definition)

    sample_data = create_sample_data()
    values = [list(asdict(data).values()) for data in sample_data]
    insert_data(session, table_name, table_definition, values)
    return f"data has been inserted into {table_name}"

$$;

call backup_backlog_data('backlog_data');

select * from backlog_data;
```

We have confirmed that our stored procedure creates table if it doesn't exist and inserts data into it. Now we need to implement data fetching from Backlog API.

>The `append` mode inserts data into a table, if the table does not exist, it creates the table. In essence, we don't have to check the existence of the table, nor create it separetely. But for modularity and readibily I am leaving the code as it is.

This post has already become too log. Let's finish the final piece of our project in [the next post][fourth-part].

[first-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-i.html
[second-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-ii.html
[third-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-iii.html
[fourth-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-iv.html
