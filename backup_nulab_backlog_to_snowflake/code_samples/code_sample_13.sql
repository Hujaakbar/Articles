CREATE OR REPLACE PROCEDURE get_latest_record(table_name VARCHAR, column_name VARCHAR)
RETURNS INTEGER
LANGUAGE PYTHON
RUNTIME_VERSION = '3.13'
PACKAGES = ('snowflake-snowpark-python', 'snowflake.core')
HANDLER = 'main' -- entry point to our handler
AS
$$
from typing import Any
import snowflake.snowpark.functions as f


def main(session, table_name: str, column_name: str) -> int | None:
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
    # returns none if there are no records
    return result[0][column_alias]

$$;

call get_latest_record('backlog_data', 'activity_id');

-- drop procedure get_latest_record(varchar, varchar);