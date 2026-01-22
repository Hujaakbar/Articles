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

call table_exists('my_table') -- use single quotes

-- In Python Stored procedure, entry point function name (`HANDLER`), Python version (`RUNTIME_VERSION`),  and packages (`PACKAGES`) should be specified in the wrapper part.

-- When you call python stored procedure, Snowflake automatically creates a Session object and passes it to the stored procedure. The entry point function should accept session object as a first argument.

