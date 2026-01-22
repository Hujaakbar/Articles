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