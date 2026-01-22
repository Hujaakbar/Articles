CREATE TASK backup_backlog_data
  SCHEDULE='60 MINUTES'
  SERVERLESS_TASK_MAX_STATEMENT_SIZE='LARGE'
  SUSPEND_TASK_AFTER_NUM_FAILURES = 1
  AS 
    call backup_backlog_data('backlog_data');

ALTER TASK backup_backlog_data resume;