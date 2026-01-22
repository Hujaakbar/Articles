# Ingesting Nulab Backlog Data Into Snowflake Tables: Part I

This tutorial have four parts in total:

- [Part One][first-part]
- [Part Two][second-part]
- [Part Three][third-part]
- [Part Four][fourth-part]

I wanted to backup Backlog data onto Snowflake tables. But there was not easy backup options, so I created one and wanted to share it with you.

In this tutorial we will extract data from Backlog and ingest it into Snowflake tables using Snowflake Stored Procedures.

[Backlog](https://nulab.com/backlog/):
: a project management software developed by a Japanese company Nulab, Inc.

[Snowflake](https://www.snowflake.com/):
: a data storage platform.

## Existing Options

It is almost always good idea to use existing tools and solutions. In other words, there is no need to reinvent the wheel. So, before trying to implement my custom solution, I wanted to explore the landscape in search of existing solutions.

Backlog only offers REST API and Web Hook endpoints, no integration or other features. As for Snowflake, although it offers variety of connection options: [Snowflake OpenFlow](https://docs.snowflake.com/en/user-guide/data-integration/openflow/connectors/about-openflow-connectors), [Snowflake connectors](https://other-docs.snowflake.com/connectors), [Snowflake Ecosystem All](https://docs.snowflake.com/en/user-guide/ecosystem-all), [Snowflake Ecosystem ETL](https://docs.snowflake.com/en/user-guide/ecosystem-etl), unfortunately as of January 2026, there is no native Backlog connector.

**There are no first-party (native) connection options, how about third-party options?**
I could find some **paid** third-party solutions such as [cdata](https://jp.cdata.com/kb/tech/backlog-sync-snowflake.rst) and [workato](https://www.workato.com/integrations/backlog~snowflake), but couldn't find any open-source tools.

If there is no existing open-source solution available, we can build our custom solution.

> Note:
> There is an awesome ETL & ELT tool called [Airbyte](https://airbyte.com/). Although it doesn't have a Backlog connecter, building Airbyte connectors is very easy. A challenging part is deploying Airbyte requires kubernetes cluster.

## Custom Solution

There are many ways to create our custom solution. The best approach is context dependent. Your requirements might be different from mine. I will introduce some of the available options, based on your own needs/requirements, you can implement one. Below I will list the interfaces provided by Snowflake and Backlog and their capabilities.

### Backlog

Backlog exposes both [REST API](https://developer.nulab.com/docs/backlog/) and [Web hook](https://support.nulab.com/hc/en-us/articles/8840133998489-How-to-add-and-manage-webhooks-in-Backlog) endpoints.

If you want to get notified as soon as some actions happen in Backlog, You should use Web hooks. In my case, however I just want to backup Backlog data to a Snowflake table. Using Backlog Rest API and calling it a few times a day suffices my requirements.

### Snowflake

- [REST API](https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/reference)
- [Native Programmatic Interfaces](https://docs.snowflake.com/en/user-guide/ecosystem-lang)
- [Stored Procedures](https://docs.snowflake.com/en/developer-guide/stored-procedure/stored-procedures-overview)

#### REST API

Although Snowflake has [REST API](https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/reference), it does not support inserting data into tables.

#### Native Programmatic Interfaces

Native Programmatic Interfaces are programming language specific SDKs (Software development Kit *libraries*) to connect to Snowflake. Nodejs, SQLAlchemy, and Python sdks  are some of the available Native Programmatic Interfaces. Check out [API Reference](https://docs.snowflake.com/en/api-reference) for details.

Native Programmatic Interfaces fit the bigger, more complex applications better. As an example, let's assume we are building a python web application that has many features and functionalities. The Application takes inputs from users, perform certain calculations, communicates with other servers etc.

At some point the application needs to get data from or record data onto Snowflake tables. For this task, we can use Snowflake Native Programmatic Interface such as Python SDK. Application connects to Snowflake using snowflake provided python library to authenticate, and execute necessary queries.

In my case, I only need to record fetched data onto a Snowflake table. No other functionality is needed. Native Programmatic Interfaces are overkill for such a simple requirement.

#### Stored procedures

Snowflake Stored Procedures are custom procedures created by users. Stored procedures are similar to functions (with some differences). Stored procedures can be written in SQL, Java, JavaScript, Python or Scala. Stored procedures are run within Snowflake (controlled cloud environment).

> Snowflake has User-defined functions as well. User defined functions are similar to stored procedures but not the same. User defined functions should be deterministic, and always return a value. While, Stored Procedures don't have to return a value, and they are most commonly used for administrative tasks such as DDL and DML.

I will talk about Stored Procedures more in [the second part][second-part] of these series.

### What to Use and Where To Run

We have a few options to create our custom solutions. Based on which mix of the options we use, we can run our custom solution in cloud providers such as AWS, GitHub, or within Snowflake.

**Option 1:** [Backlog webhook + Snowflake Native Programmatic Interfaces] runs on AWS lambda functions.
Whenever new event occurs in the Backlog, Backlog webhook calls lambda function, lambda function records data on Snowflake table immediately using Native Programmatic Interfaces.

**Option 2:** [Backlog REST API + Snowflake Native Programmatic Interfaces] runs on GitHub Actions.
A script executed by GitHub Actions calls Backlog Rest API periodically (e.g. every two hours), and records all the events of Backlog that happened since its last run onto Snowflake using Native Programmatic Interfaces.

**Option 3:** [Snowflake Stored Procedures + Backlog REST API] runs on Snowflake.
[Snowflake Tasks](https://docs.snowflake.com/en/user-guide/tasks-intro) executes Snowflake Stored Procedure periodically. Stored Procedure calls Backlog REST API and records the fetched data onto Snowflake table.

Choose option No 2, if you prioritize easy version controlling, deployment, code review and modifications to code. Choose Snowflake Stored Procedures option if you want to confine and control code, roles, permissions and secrets in one place.

> Note: If you choose Snowflake Stored Procedures option, there will be a friction in code deployment and updates.

In this tutorial, we will go with Snowflake Stored Procedures option. For implementation details, proceed to [the part two][second-part].

[first-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-i.html
[second-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-ii.html
[third-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-iii.html
[fourth-part]: https://blog.hujaakbar.com/2026/01/ingesting-nulab-backlog-data-into-snowflake-tables-part-iv.html
