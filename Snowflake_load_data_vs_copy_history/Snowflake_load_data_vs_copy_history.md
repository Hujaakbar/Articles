# Snowflake Load History vs Copy History: 7 differences

![data](./images/history.jpg)
_Image by [Icons8_team](https://pixabay.com/users/icons8_team-6332517/?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=3435879") from [Pixabay](https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=image&utm_content=3435879)_

Tracking data loads in Snowflake is crucial to maintaining data health and performance. Load History and Copy History are features that provide valuable information about past data loads. Understanding these features can help you efficiently troubleshoot, audit, and analyze performance.

You might be wondering why two functions exist to achieve the same goal? What are the differences and which one you are supposed to use and when ?
In this article we will provide you with the all the answers. So, let's learn what are the differences and when to use which!

## Load History vs Copy History: 7 differences

### Differences １ and 2: views vs table function and Account Usage vs information Schema

Here things get little confusing, bare with me, there are two Load History views, a [view](https://docs.snowflake.com/en/sql-reference/info-schema/load_history) that belongs to [Information Schema](https://docs.snowflake.com/en/sql-reference/info-schema) and a [view](https://docs.snowflake.com/en/sql-reference/account-usage/load_history) that belongs to [Account Usage schema](https://docs.snowflake.com/en/sql-reference/account-usage). As for Copy History, there are Copy History [table function](https://docs.snowflake.com/en/sql-reference/functions/copy_history) of Information schema and a Copy History [view](https://docs.snowflake.com/en/sql-reference/account-usage/copy_history) of Account Usage schema.

| Information Schema          | Account Usage     |
| :-------------------------- | :---------------- |
| Load History View           | Load History View |
| Copy History Table Function | Copy History View |

Load History of Information Schema example：

```sql
use database db_1;

select table_name, last_load_time
  from information_schema.load_history
  where schema_name = current_schema() and
  table_name='TABLE_1';
```

Load History of Account Usage example：

```sql
use database db_1;

select table_name, last_load_time
  from snowflake.account_usage.load_history
  where schema_name = current_schema() and
  table_name='TABLE_1';
```

Copy History **view** example:

```sql
select table_name, last_load_time
from snowflake.account_usage.copy_history
  where schema_name = current_schema() and
  table_name='TABLE_1';
;
```

Pay attention the way you query Copy History **view** and Load History views is almost identical.

Copy History **table function** example:

```sql
select *
from table(
    information_schema.copy_history(
        TABLE_NAME=>'TABLE_1',
        START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())
        )
    )
;
```

### Difference 3: query syntax and the number of tables that can be specified

If you haven't already noticed, let me clarify that using both Load History and Copy History views you can query load history of more than one table. But with Copy history table function, you are limited to querying load history of a single table at a time. Table name in Copy History table function is **required**.

Example：

Below query only returns load history of `Table_1`.

```sql
select *
from table(
    information_schema.copy_history(
        TABLE_NAME=>'TABLE_1',
        START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())
        )
    )
;
```

Below query returns load history of (up to) 10 tables.

```sql
USE DATABASE database_a;

SELECT table_name, last_load_time
  FROM information_schema.load_history
  ORDER BY last_load_time DESC
  LIMIT 10;
```

### Difference 4: Latency

Copy History and Load History **views** of Account Usage have latency between the latest changes and when those changes are reflected in these views. To be more precises, Copy History view of Account Usage has up to 120 minute latency and Load History view of Account Usage has up to 90 minute latency in most of the cases.
But latency might be up to **two** days if both of the following conditions are met:

-   Fewer than 32 DML statements have been added to the given table since it was last updated in COPY_HISTORY/LOAD_HISTORY.

-   Fewer than 100 rows have been added to the given table since it was last updated in COPY_HISTORY/LOAD_HISTORY.

As for Load History view of Information Schema and Copy History **table function** there is no latency.

| Source                                  | Latency of Data                         |
| :-------------------------------------- | :-------------------------------------- |
| Copy History **view**                   | usually 120 minutes <br> (up to 2 days) |
| Load History view of Account Usage      | usually 90 minutes <br> (up to 2 days)  |
| Load History view of Information Schema | No latency                              |
| Copy History **table function**         | No latency                              |

If you need latest data with no latency, you had better use either Load History view of Information Schema or Copy History **table function**.

### Difference 5: Retention Period

Load History view of Information Schema and Copy History **table function** retains historic data for 14 days.
Copy History **view** and Load History view of Account Usage retain historic data for 1 year (365 days).

| Source                                  | Data Retention |
| :-------------------------------------- | :------------- |
| Copy History **view**                   | 365 days       |
| Load History view of Account Usage      | 365 days       |
| Load History view of Information Schema | 14 days        |
| Copy History **table function**         | 14 days        |

### Difference 6: Tracking the history of data loaded using Snowpipe

Load History views (of both Information Schema and Account Usage) do **NOT** return the history of data loaded using [Snowpipe](https://docs.snowflake.com/en/user-guide/data-load-snowpipe-intro), it only returns the history of data lated using [COPY INTO](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) command. While both Copy History table function and view return the history of data loaded using Snowpipe and `Copy INTO` command.

Snowpipe is used in continuous loading.

> Snowpipe enables loading data from files as soon as they’re available in a stage.

| Source                                  | Load history type           |
| :-------------------------------------- | :-------------------------- |
| Copy History **view**                   | `COPY INTO`<br>and Snowpipe |
| Load History view of Account Usage      | `COPY INTO` only            |
| Load History view of Information Schema | `COPY INTO` only            |
| Copy History **table function**         | `COPY INTO`<br>and Snowpipe |

### Difference 7: the maximum number of rows returned

Load History of Information Schema returns an upper limit of 10,000 rows. Copy History table function, Copy History view and Load History of Account Usage do not have this limit.

---

## Summary

As you can see all have distinct features. To quickly grasp the differences among them, you can refer to the below table that summaries all the features of the Load History, Copy History views and Copy History table function.

| Differences                       | Load History                         | Copy History                          | Load History       | Copy History                |
| :-------------------------------- | :----------------------------------- | :------------------------------------ | :----------------- | :-------------------------- |
| View or Table function            | view                                 | view                                  | view               | table function              |
| Schema they belong to             | Account Usage                        | Account Usage                         | Information Schema | Information Schema          |
| Multiple tables<br>can be queried | Yes                                  | Yes                                   | Yes                | No                          |
| Data Retention                    | 365 days                             | 365 days                              | 14 days            | 14 days                     |
| Latency                           | usually 90 minutes<br>(up to 2 days) | usually 120 minutes<br>(up to 2 days) | No latency         | No latency                  |
| Load history type                 | `COPY INTO` only                     | `COPY INTO`<br>and Snowpipe           | `COPY INTO` only   | `COPY INTO`<br>and Snowpipe |
| Maximum number of rows returned   | No limit                             | No limit                              | 10,000             | No limit                    |

-   I would recommend using Copy History view if you need load history data that is older than 2 days.
-   Use Copy history table function if you need load history data of a single table with no latency.
-   Use Load History view of Information schema if you need to query load history data of multiple tables with no latency.
