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