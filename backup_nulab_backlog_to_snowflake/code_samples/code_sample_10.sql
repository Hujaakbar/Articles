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
