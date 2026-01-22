Create or replace procedure fetch_data_from_backlog()
  returns varchar
  language python
  runtime_version = 3.13
  secrets = ('api_key' = backlog_api_key)
  external_access_integrations = (backlog_api_access_integration)
  packages = ('snowflake-snowpark-python','requests')
  handler = 'main'
as
$$
import requests
from _snowflake import get_generic_secret_string

def main(session):
    backlog_api_key = get_generic_secret_string('api_key')
    endpoint = "https://<my-org>.backlog.com/api/v2/space/activities"
    with requests.Session() as s:
        response = s.get(url=endpoint, params = {"apiKey": backlog_api_key, "count": 2})
        if response.status_code != 200:
            return response.text
        return response.json()
$$;

call fetch_data_from_backlog();

-- drop procedure fetch_data_from_backlog();