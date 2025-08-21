# dbt core

dbt stands for data build tool. [dbt core](https://github.com/dbt-labs/dbt-core) is an open source cli tool, written in python, that is intended for data transformation purposes. There is also a cloud hosted (paid) version called dbt cloud. However, in this post we will discuss dbt core (free open-source tool).

We can think of dbt core as an sql client. It connects to the server and server executes the code. It has certain features to make the data transformation process easy to manage. However, there is a critical distinction, dbt core is intended to be used for creating tables and views, **not** for querying, deleting or dropping them.

> dbt core is used for ***transforming*** data.

Before explaining dbt core any further, first, let's clarify what data transformation means.
Imagine you work at a company as a data engineer. Your company gathers data coming from APIs, excel, csv files, customers, suppliers, internal systems and more.
This data might be useful to gain valuable insights into company's operations.

As a first step you extract and load all the available data into data warehouses (like Snowflake, DataBricks, BigQuery etc) in a **tabular** format.
This data is called **raw data**, because you are storing this data as it is without modifying or transforming it.

When your sales/marketing or business analytics team wants to use this data to gain business insights into company's operations, they have to write complex queries to filter out unnecessary data, modify data or change the format of the data. This is the issue. They are not data engineers, writing complex sql queries is not their strong suit.

To make life easier for your colleagues, as a second step, you **t**ransform the raw data into categorized data in the form of new views or tables by filtering out, modifying or formatting certain parts of it. (This transformation is achieved via filtering rows, grouping rows, renaming columns, calculating new values based off of existing values etc.)

dbt core can help you in this second, data transformation, step.
It helps you organize your code and project structure neatly and provides you with shortcuts that would otherwise require complex sql scripts.

To summarize:

- dbt operates on data that has already been loaded into the data platforms (Snowflake, Databricks etc.)
- This raw data needs to be in a structured format, typically tables
- We write the transformation code in a structured way using sql & [jinja](https://jinja.palletsprojects.com/) syntax
- dbt core parses and compiles the code and sends it to the data platform
- data platform executes the code (creates new tables & views)

## Main Concepts and Features

- [models](#models)
- [jinja](#jinja-functions)
- [macros](#macros)
- [hooks](#hooks)
- [tests](#tests)
- [docs](#docs)
- [analysis](#analysis-files)

> Note: dbt operates on data that has already been loaded into the data warehouse. This raw data needs to be in a structured format, typically tables.

**Key Takeaways:**

- In dbt you only write `Select` statements, dbt wraps your `select` statements with `create` boilerplate code.
- The sql statements should be written using the sql dialect compatible with your chosen platform. If you are using Snowflake, then you should use Snowflake compatible sql.
- Jinja can be used extensively in dbt project including config files and sql statements.

### Models

An SQL file that contains `select` statement and intended to be executed is called [**model**](https://docs.getdbt.com/docs/build/sql-models).
dbt wraps the `select` statements with `create` boilerplate code.

> Note: Model files should be placed in `models` folder.

Imagine we have a raw table named `raw_sales_data` with below columns:

1. order_id
1. customer_id
1. product_id
1. order_date
1. quantity
1. price
1. discount_percentage
1. shipping_address
1. payment_method
1. product_category
1. region
1. is_online_order
1. delivery_status
1. customer_segment
1. feedback_score
1. purchase_channel
1. promotion_code
1. employee_id
1. return_reason

We want to transform the records of `raw_sales_data` table (by creating a new view called "simple_sales_data"):

`models/simple_sales_data.sql`

```sql
SELECT
    order_id,
    customer_id,
    product_id,
    quantity * price as order_value,
    CURRENT_TIMESTAMP() AS processed_at
FROM
    raw_sales_data
WHERE
    order_date >= '2024-01-01' AND order_date < '2024-04-10'
```

dbt parses and compiles our code to below code:

```sql
create or replace view <db_name>.<schema_name>.simple_sales_data
  as (
    SELECT
    order_id,
    customer_id,
    product_id,
    quantity * price as order_value,
    CURRENT_TIMESTAMP() AS processed_at
FROM
   raw_sales_data
WHERE
    order_date >= '2024-01-01' AND order_date < '2024-04-10'
  );
```

As we can see, dbt wraps our code with platform specific `create` boilerplate code.

The name of view/table to be created is determined based on the model filename. Model names are case-sensitive. Model files can be placed in subdirectories inside the `models` folder.

### Materialization

Creation of database objects such as views and tables from models is called materialization. By default dbt models are created (materialized) as views. Sometimes we may want to create tables instead of views.

Available materialization options:

- view (default)
- table
- incremental (table)
- ephemeral
- materialized_view

Below are the explanation of some of the materialization options.

**Incremental**
: [incremental models](https://docs.getdbt.com/docs/build/incremental-models) are materialized as tables. The first time a model is run, all the rows of the source table are transformed (inserted into the target table with the transformation logic). In the subsequent runs, only the new or updated rows of the source table will be transformed and inserted into the target table. This improves performance and saves compute costs.
: To select only new or updated rows, we should write the filtering logic (`where` clause). ([Example](#incremental-models-materialization) will be provided in later section of this post.)

**Ephemeral**
: [ephemeral models](https://docs.getdbt.com/docs/build/materializations#ephemeral) will be parsed & compiled into a common table expression (CTE).
What it means is ephemeral models won't be created on the data platform.
Ephemeral models are meant to be used with other (dependent) models.
: Ephemeral models help us to keep our project modularized and reusable.

Your data platform might allow additional materialization options. For more info, check their documentation.

> Note: using dbt core, although we can replace, we cannot drop tables or views. We have to do it manually in our database platform.

We will learn how to [configure materialization](#model-configuration) options in later sections of this tutorial.

### Jinja

Models can include [jinja](https://jinja.palletsprojects.com/en/stable/) syntax. Jinja can help us with repetitive code blocks, configurations and more.

`models/US_Customer_Orders.sql`

```sql
Select
    {% for customer_number in range(1, 6) %}
        cust_{{customer_number}} as USA_Customer{{customer_number}},
        cust_{{customer_number}}_ord as USA_Customer{{customer_number}}_order
        {% if not loop.last %},{% endif %}
    {% endfor %}
from customers
where country = 'USA';
```

Above code will be parsed and compiled into below code and sent to the data platform:

```sql
create or replace view <db_name>.<schema_name>.US_Customer_Orders
  as (
    Select
        cust_1 as USA_Customer1,
        cust_1_ord as USA_Customer1_order,

        cust_2 as USA_Customer2,
        cust_2_ord as USA_Customer2_order,

        cust_3 as USA_Customer3,
        cust_3_ord as USA_Customer3_order,

        cust_4 as USA_Customer4,
        cust_4_ord as USA_Customer4_order,

        cust_5 as USA_Customer5,
        cust_5_ord as USA_Customer5_order

    from customers
    where country = 'USA'
    );
```

### Configuration

dbt offers a highly flexible configuration system. This flexibility may cause some confusion in the beginning. I will talk about how to [set up dbt](#set-up-and-configuration) and configure it in detail later in this tutorial.
Now, however, I want to give you high level overview of the configuration options.

dbt can be configured at three levels.

1. `dbt_project.yml` file (configuration for entire project)
1. `*.yml` file (configurations for single & multiple files)
1. `config()` jinja function within the model files (model specific configurations)

Let's clarify "`*.yml` file" option.

To configure the project and build the parsed sql files, dbt uses `dbt_project.yml` file, `config` section of the model files, and any yaml file.

The `.yml` files can be named anything. In this tutorial we name them `properties.yml`. These files should usually be placed in the same folder as the models they target. dbt parses the contents of these `.yml` files, along with the `dbt_project.yml` and `config` function and applies the configurations with the below precedence:

1. `config()` jinja function within the model files
2. `.yml` config files
3. `dbt_project.yml` project config file

### Jinja Functions

Jinja syntax can be used almost anywhere (tests, models, config files, docs) in dbt project.
dbt team extended jinja by adding dbt specific functions as well such as `ref`,  `docs` blocks, `snapshots`, `logs` and many more.
You can check out the full list of [dbt specific jinja functions](https://docs.getdbt.com/reference/dbt-jinja-functions).

I highlight some of the dbt features made possible thanks to Jinja.

#### ref()

We can refer to a model as if we are referring to a table or view using [`ref()` function](https://docs.getdbt.com/reference/dbt-jinja-functions/ref).
`ref(model_name)` works with unique names. Make sure your model names don't clash.

`models/customers.sql`

```sql
select
  id as customer_id,
  name
from db_xyz.schema_abc.raw_customer_data
```

We can refer to the `customers.sql` model in below `orders.sql` model.

`models/orders.sql`

```sql
Select
  id as order_id,
  order_date,
  customer.name as customer_name
from db_xyz.schema_abc.raw_order_data
inner join {{ ref('customers') }} as customer
using(customer_id)
```

What happens:
dbt replaces the `{{ ref('customers') }}` with correct `<dbt_name>.<schema_name>.customers` view name.

Execution order:

1. On the data platform `customers` view is created.
1. After that `orders` view is created.

dbt also uses `ref` function to create dependency graph in generated documentation.

#### source()

Instead of hard coding database and schema names in each model, we can define them in a yaml file and refer to them in our model files using [`source()` function](https://docs.getdbt.com/reference/dbt-jinja-functions/source).

```python
source('source_name', 'table_name')
```

Sources are defined in yaml file and this yaml file can reside anywhere within `models` folder.

`models/sources.yml`

```yaml
version: 2

sources:
  - name: sales_prod # name of the source
    database: PROD_SALES_DB
    schema: RAW_SALES
    tables:
      - name: accounts
      - name: opportunities

    - name: sales_contracts # name of the source
      database: PROD_SALES_DB
      schema: contracts
      tables:
        - name: orders
        - name: shipments

  - name: sales_archive # name of the source
    database: ARCHIVE_SALES_DB
    schema: RAW_SALES
    tables:
      - name: accounts
      - name: opportunities
```

Note: One source can have only one database and one schema.

refer to the sources in model file:

`models/orders/order_by_customers.sql`

```sql
select
  account_id,
  order_id,
  ...
from {{ source('sales_archive', 'accounts') }}
```

dbt constructs the fully qualified table reference using above information.

It compiles above code into below sql script:

```sql
select
  account_id,
  order_id,
  ...
from ARCHIVE_SALES_DB.RAW_SALES.accounts
```

If, for whatever reason, the location of the tables change in our data platform (database name or schema name changes), we only need to modify this yaml file, no need to modify model files.

#### Macros

Macros are similar to functions. Macros can take arguments and return a value. A return value can be a multiple lines of text/code.

Macros start with `{% macro %}` block and they are defined in `.sql` files inside `macros` folder.

creating macro:

```jinja
{% macro macro_name(argument1, argument2 ...) %}
    return_value
{% endmacro %}
```

Macro call will be replaced with macro's return value.

Example:

`macros/fix_string.sql`

```sql
{% macro fix_string(column_name) %}
    upper(trim(coalesce(column_name, ''))) as column_name
{% endmacro %}
```

Calling above macro:

`models/sales_by_department.sql`

```sql
select
  id as user_id,
  {{ fix_string(username) }},
  {{ fix_string(department) }}
  ...
from sales_data
```

compiled sql will be

```sql
select
  id as user_id,
  upper(trim(coalesce(username, ''))) as username,
  upper(trim(coalesce(department, '')))  as department
  ...
from sales_data
```

##### config()

Dbt has many built in macros. One of them is `config` macro that is used to configure models individually.

```sql
{{ config(materialized='table') }}

select
    id as user_id
    ...
from customers

```

dbt has over 600 built-in macros. In addition to them, there are packages such as [dbt-utils](https://github.com/dbt-labs/dbt-utils?#generic-tests) that has many more macros available.

##### Hooks

If we have to run certain code before and/or after each model run, we can use [hooks](https://docs.getdbt.com/docs/build/hooks-operations). Hooks are snippets of SQL code that are run at the start or end of each model or at the start or end of each dbt execution commands.

[pre-hook & post-hook](https://docs.getdbt.com/reference/resource-configs/pre-hook-post-hook): run at the start or end of each model.
[on-run-start & on-run-end](https://docs.getdbt.com/reference/project-configs/on-run-start-on-run-end): run at the start or end of each `dbt run`/`dbt test`/`dbt docs generate` etc commands

Hooks can be a single sql statement or a **list** of multiple sql statements

Syntax:

`dbt_project.yml`

```yaml
models:
  my_dbt_demo: # dbt project name (so that this config does not apply to installed packages)
    # runs before and after each `dbt run`/`dbt test`/`dbt docs generate` commands
    on-run-start: sql-statement |  [SQL-statement, SQL-statement, ...]
    on-run-end: sql-statement |  [SQL-statement, SQL-statement, ...]

    # runs before and after each model run/execution
    additional_permission_needed_models:
      +pre-hook: SQL-statement | [SQL-statement, SQL-statement, ...]
      +post-hook: SQL-statement | [SQL-statement, SQL-statement, ...]
```

`models/<model_name>.sql`

```sql
{{ config(
    pre_hook="SQL-statement" | [SQL-statement, SQL-statement, ...],
    post_hook="SQL-statement" | [SQL-statement, SQL-statement, ...],
) }}

select
  ...
from {{ source("source_name", "table_name") }}
```

`models/properties.yml`

```yaml
models:
  - name: customers
    config:
      pre_hook: <sql-statement> | [<sql-statement>]
      post_hook: <sql-statement> | [<sql-statement>]
```

Example:

```yaml
models:
  my_dbt_demo:
    # runs before and after each model run/execution
    additional_permission_needed_models:
      +pre-hook: "grant usage on schema {{ target.schema }} to role env_var('PROD_USER');"
```

We can also call a macro inside a hook.

Note: Hooks are cumulative. If we define hooks in both `dbt_project.yml` and in the `config` block of a model, both sets of hooks will be executed.

##### var()

Variables can be passed from the `dbt_project.yml` file into models.

To define a variable in our project, we need to add the `vars` keyword to `dbt_project.yml` file.

`dbt_project.yml`

```yaml
name: dbt_2025_project
version: 1.0.0

... # some config here

# variables syntax:
# key: value
vars:
  year_end_month: 03 # march
```

using vars in models

`models/customer_voice.sql`

```sql
select
  *
from financial_reports
where received_month = {{ var("year_end_month") }}
```

The var() function takes an optional second argument as an default value.

`models/customer_voice.sql`

```sql
select
  *
from contact_emails
where category = '{{ var("focus_customer_email_category", "complaint") }}'
```

##### log()

dbt automatically generates logs. In addition to automatically emitted logs, we can write log statements in models and macros. Log (output) files are located inside `logs` folder.

`models/inventory.sql`

```sql
{% log('hello world') %}

select
  ...
from inventory_data
```

### Tests

We can test our models. [dbt tests](https://docs.getdbt.com/docs/build/data-tests) are `select` statements written in sql and jinja.

How tests are used:

1. We create our models (transformation logic)

    `models/marketing_budget.sql`

    ```sql
    select
        id as campaign_id,
        campaign_budget,
        campaign_cost
    from raw_marketing_data
    ```

    Assume the total `campaign_budget` should be higher than total `campaign_cost`.
    We can write a test for it.

1. A singular test (targeting specific model)

    `tests/marketing_budget_test.sql`

    ```sql
    with totals as
    (select
        sum(campaign_budget) as total_campaign_budget,
        sum(campaign_cost) as total_campaign_cost
    from {{ ref('marketing_budget') }} -- model name
    )
    select *
    from totals
    where total_campaign_cost >  total_campaign_budget
    ```

    Above query returns rows if and only if `total_campaign_cost` is higher than `total_campaign_budget`, meaning marketing went over-budget.
    dbt runs this test, and shows "success" if no rows are returned, "failure" if test queries return any record.

Note: do not add semicolon in test queries.

Tests that target specific resources are called singular tests. We place our test files under `tests` folder.

To summarize, dbt tests are sql queries (`select` statements) that try to catch records models shouldn't have.
`dbt test` command **automatically** runs all the singular test files inside the `tests` folder.

#### Generic Data Tests

We have seen a singular test. Singular tests target only specific models.
Often times what we want to test is very common among models, such as certain columns are unique or not null.
For these common scenarios, we don't have to write singular tests, instead we can use generic data tests provided by dbt. Generic data tests can be reused.

dbt provides below generic tests out of the box:

- `unique`
- `not_null`
- `accepted_values`
- `relationships`

All we need to do is to specify that we want to run these tests against our models.
We do so using `.yml` file inside `models` folder.

Note: We can test not only models but also [seeds](#seeds), and [sources](#source). Collectively models, seeds, sources, snapshots, analyses are called recourses. They will be explained later.

`models/properties.yml`

```yaml
version: 2

models:
  - name: events # events model
    columns:
      - name: event_id
        data_tests:
          - unique:
              config: # config is optional
                where: "place = 'London'" # where clause is optional

      - name: event_code
        data_tests:
          - not_null

      - name: status
        data_tests:
          - accepted_values:
              arguments:
                values: ['held', 'pending', 'waiting for approval']

      - name: venue
        data_tests:
          - not_null
          - relationships:
              arguments:
                to: ref('venues')
                field: venue_id

  - name: venues # venues model
    columns:
      - name: venue_id
        data_tests:
          - unique
          - not_null

      - name: capacity
        data_tests:
          arguments:
            accepted_values: [10000, 15000, 20000]
            quote: false # dbt will treat the list of accepted values as strings, to change that, set quote to false
```

Above file contains tests for two models, 'venues.sql' and 'events.sql'.
It tests :

1. `events.event_id` is unique for London area.
1. `events.code` is not null
1. `events.status` column contain only one of the given values 'held', 'pending', 'waiting for approval'.
1. `events.venue` column is not null and references valid values from `venues.venue_id` column (foreign key test).
1. `venues.venue_id` column are unique and not null
1. `venues.capacity` column values are one of the 10000, 15000, 20000 values.

To run above tests, run `dbt test` command.
dbt runs all the tests, and shows how many tests have succeeded and how many of them have failed.

In addition to above four generic tests, we can find other tests in packages such as [dbt-utils](https://github.com/dbt-labs/dbt-utils?#generic-tests).

##### Generic tests for resources

We have seen generic tests targeting a single column. But sometimes we might need to test a set of columns together. Packages like [dbt-utils](https://github.com/dbt-labs/dbt-utils?#generic-tests) provide us with such generic tests. (We will learn how to add these packages later.)

In `deliveries.sql` model `actual_time_took` column values should be smaller or equal to `projected_time` column values when no issue occurred.

`models/deliveries.sql`

```sql
{{ config(materialized='table') }}

select
  projected_time,
  actual_time_took,
  issue
from {{ source('main', 'orders' )}}
```

`models/deliveries.yml`

```yml
version: 2

models:
  - name: deliveries
    description: 'Store the projected time and actual time it took to deliver the goods'
    data_tests:
      - dbt_utils.expression_is_true:
          expression: "actual_time_took <= projected_time"
          config:
              where: 'issue = "" '
```

Note: As the test name suggest, `dbt_utils.expression_is_true`, we will test if the expression is true.

#### Creating Generic Tests

In addition to already provided generic tests, we can write our own generic tests as well. All generic tests should accept one or both of the standard arguments: `model_name` and `column_name`.

For example, let's say, we want to have a generic test that checks whether a column value is positive.
We can do so using `test` block like below.

`macros/generic_tests/positive.sql`

```sql
{% test positive(model, column_name) %}
    select
        {{ column_name }}
    from {{model}}
    where {{ column_name }} < 0
{% endtest %}
```

Remember to test a model, query for records that model shouldn't have.

We can use our test:

`models/properties.yml`

```yaml
version: 2

model:
 - name: employees
   columns:
    - name: age
      data_tests:
          - positive
```

Our test will be parsed & compiled into below query.

```sql
select
      age
from <dbt_name>.<schema_name>.employees
where age < 0
```

If you want to create a generic test that accepts more than two arguments, you can check [this page](https://docs.getdbt.com/best-practices/writing-custom-generic-tests).

### Docs

dbt can generate documentation (docs) from the resource files, configuration files, table/view metadata provided by data platform and more. dbt generates a documentation website to display docs.
To generate more comprehensive documentation, we can add descriptions in `yml` files, and dbt incorporates these descriptions into the generated docs.

`models/properties.yml`

```yml
version: 2

models:
  - name: events
    description: "This table contains marketing campaign events"
    columns:
      - name: event_id
        description: "This is a unique identifier for the event"
        data_tests:
          - unique
          - not_null
          - positive:
            description: "This is a custom test."
        ...

  - name: stuff
    description: "all the employees in the company"
    columns:
      - name: id
        description: "The employee_id who works in the company"
        data_tests:
          - not_null
```

As you can see, we can write descriptions on models, columns, generic tests and so on. We can write descriptions for singular test files as well.

`tests/singular/properties.yml`

```yaml
version: 2
data_tests:
  - name: joined_left_test
    description: 'This test asserts all "leave" dates are bigger than "join" dates'
```

We can also write much longer descriptions, using `.md` files referred to as `doc` files. Doc files should include `{% docs %}` jinja block and can include markdown code.

`docs/events.md`

```jinja
{% docs campaign_events %}

# Campaign events

**Marketing Campaign events held in below cities:**

- London, UK
- Tokyo, Japan

{% enddocs %}
```

Include above docs in `models/properties.yml` file.

```yaml
version: 2

models:
  - name: events
    description: '{{ docs("campaign_events") }}'
    columns:
      - name: event_id
        description: 'This is a unique identifier for the event'
        data_tests:
          - unique
          - not_null
        ...
```

Technically, we don't have to keep our `doc` files inside the `docs` folder. By default, dbt will search for docs in all resource paths. We can keep them near the model they describe.

If we want to keep all the doc files exclusively inside the `docs` folder, we can specify it in `dbt_projects.yml` file.
After we do so, dbt only searches for `docs` folder for doc files.

`dbt_project.yml`

```yml
# some config
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
macro-paths: ["macros"]
# other paths ...
docs-paths: ["docs"]
# more config...
```

To generate documentation, we need to run [`dbt docs generate` command](https://docs.getdbt.com/reference/commands/cmd-docs). When we run this command, dbt creates `index.html` and a few other related json files inside the `target` folder. To serve this html file, we need to run `dbt docs serve` command. It serves the contents of the doc website at `127.0.0.1`.

- Run `dbt docs generate` command to generate documentation site
- Run `dbt docs serve` command to serve and open the documentation site in the browser

Note: This is not a static page.

To create a static page, we need to pass `--static` option to `dbt docs generate` command. It creates a single page, `index.html` file that includes all the necessary data.

```bash
dbt docs generate --static
```

### Seeds

dbt is used for transforming data, not loading it to data platforms. But it can do so when necessary.

dbt refers to csv files as [`seeds`](https://docs.getdbt.com/docs/build/seeds).
`dbt seed` command loads the contents of a csv file into a data platform by creating a new table with the same name as a `seed` filename. Seed files are stored in `seeds` folder.

`seeds/capitals.csv`

```csv
Country, Capital
Japan, Tokyo
France, Paris
China, Beijing
...
```

dbt will infer the datatype for each column based on the data in our CSV file. We can also specify column data type in `seeds/properties.yml` file along with other configuration options.

`seeds/properties.yml`

```yaml
version: 2

seeds:
  - name: capitals
    description: "countries and their capitals"
    config:
      database: prod_dbt
      schema: common
      quote_columns: false
      column_types:
        - Country: varchar(32)
        - Capital: varchar(32)
      delimiter: ","

    # we can include data tests as well
    columns:
      - name: Country
        data_tests:
          - not_null

```

When we run `dbt seed` command, it creates a new table named `capitals` in our data platform.

Similar to models, we can refer to seeds with `ref` function in our models.

Note: loading csv files is not one of the main functionalities of the dbt. Use dbt only to load small csv files.

We can [configure `seeds`](https://docs.getdbt.com/reference/seed-configs) in `dbt_project.yml` file as well.

`dbt_project.yml`

```yaml
seeds:
  static_data: # a folder name
    +database: prod_dbt
    +schema: common
    +quote_columns: false

  colors: # colors seed
    +database: stage_dbt
    +schema: sample
    +quote_columns: true
    +column_types:
      - name: VARCHAR(32)
      - hex_code: VARCHAR(8)
    +delimiter: ":"
```

Above configuration applies to all the `seed` files in `seeds/static_data` folder and `seeds/colors.csv` file.

```txt
...
├── dbt_project.yml
└── seeds
    ├── static_data
    └── colors.csv
```

### Analysis files

If we want to write models but not run them, we should keep them under `Analysis` folder. dbt compiles these [analysis files](https://docs.getdbt.com/docs/build/analyses), but does not execute/run them.

We can find the compiled version inside `target/compiled` folder.

`analyses/order_accounts.sql`

```sql
  select
    {{ macro_name(column) }}
    ...
  from {{ ref('some_model_name') }}
```

### Packages

dbt has many features available out of the box. But we can extend dbt's testing and macro utilities even further via [packages](https://hub.getdbt.com/).

Below are some of the popular dbt packages.

- [dbt project evaluator](https://hub.getdbt.com/dbt-labs/dbt_project_evaluator/latest/): it highlights areas of a dbt project that are misaligned with dbt Labs' best practices.
- [dbt-utils](https://github.com/dbt-labs/dbt-utils): dbt utility functions (tests and macros)
- [codegen](https://hub.getdbt.com/dbt-labs/codegen/latest/): collections of macros that generate dbt code

Above packages are developed by dbt-labs.

You can find more packages at [package hub](https://hub.getdbt.com/).

#### How to Add Packages

To add a package, inside dbt project folder, we create `dependencies.yml` or `packages.yml` file. It should be at the same location as our `dbt_project.yml` file.

Inside the `dependencies.yml` or `packages.yml` file, we specify the packages we want to install.

`packages.yml`

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.3.0
```

Run `dbt deps` command to install the packages.

> dbt-utils package includes tests and macros such as
>
> - `equal_rowcount` test that asserts two joined tables/views have the same number of rows
> - `deduplicate` macro that returns the sql code required to remove duplicate rows from a source.

### dbt re-runs

dbt keeps materializing models in each run.

Let's say we have a `customers` model that is already materialized as a table. We create a new (unrelated) model, `feedback` (as a view) in `models` folder. When we run `dbt run` command, dbt creates `feedback` view and re-creates `customers` table.

*(Since the `customers` table already exists on the data platform, dbt first creates the new table with temporary name. After that, within a single transaction, it drops `customers` table and renames our newly created table to `customers`)*

If the models are materialized as views, it is not a big deal. But performance and cost related issues may arise when models are re-materialized as tables when we don't intend to.

Solution: excluding models from `dbt run` command

```bash
dbt run --exclude customers

# or

dbt run --select feedback
```

Another solution is using `incremental` materialization option.

---

## Set up and Configuration

We discussed the core concepts of the dbt, now it is time to put it into the action.
Bad news is we need an account in any of the data platforms (Snowflake, DataBricks, BigQuery etc). Good news is most of these platforms offer generous free trials.

Note: dbt core is not just a cli tool, it is a framework. What it means is that, it expects us to organize our code in a certain way and store our files in certain folders. No need to worry, dbt helps us with creating this folder structure.

### Installation

dbt core is a open-source cli tool written in python. Before installing dbt core, make sure you have python (version 3.7 or higher) already installed. It is recommended to create python virtual environment before installing dbt.

Installing dbt core:

```bash
pip install dbt-core

# check if it is installed successfully
dbt --version

# it returns information something like below
Core:
  - installed: 1.10.3
  - latest:    1.10.3 - Up to date!
```

If you are using [uv](https://docs.astral.sh/uv/) instead of pip:

```bash
# create uv environment
uv init --name dbt_databricks_demo --description "demoing dbt-core features with DataBricks platform"
uv add dbt-core

# check dbt is installed successfully
uv run dbt --version
```

#### Adapters

dbt core parses & compiles our sql & jinja code and sends it to our data platform to be executed. For this an adapter is needed.

dbt core needs an adapter:

1. to wrap our models with `create` sql statements that is compatible with the dialect of our data platform
1. to connect/send compiled models to the data platform

In this example we use Databricks as our data platform of choice. If you are using different data platform, you can check out [available adapters](https://docs.getdbt.com/docs/available-adapters).

Installing [databricks adapter](https://github.com/databricks/dbt-databricks):

```bash
pip install dbt-databricks
```

If you are using uv instead of pip:

```bash
uv add dbt-databricks
```

### Setting up dbt core project

We have necessary tools, it is time to start to use them. To set up a dbt project, run below command.

```bash
dbt init <project_name>
# e.g. dbt init dbt_databricks_demo

# if using uv
# uv run dbt init <project_name>

04:58:48  Running with dbt=1.10.3
04:58:48
Our new dbt project "dbt_databricks_demo" was created!

For more information on how to configure the profiles.yml file,
please consult the dbt documentation here:
  https://docs.getdbt.com/docs/configure-Our-profile

Happy modeling!
```

After that, it prompts us for credentials and other info to set up a profile. (Profile is a yaml file that stores data necessary to connect to the data platform.)

Example:

```bash
04:58:48  Setting up your profile.
Which database would we like to use?
[1] databricks

Enter a number: 1
# more prompts
```

Using the the data we entered, dbt creates `profiles.yml` file under `~/.dbt` directory.

It also creates two folders, in this case, `dbt_databricks_demo` (the project name we gave while creating the dbt project) and `logs` in the current directory.

Folder structure:

```bash
dbt_databricks_demo
   └─── analyses
   └─── macros
   └─── models
       └─── example
   └─── seeds
   └─── snapshots
   └─── tests
   └─── .gitignore
   └─── dbt_project.yml
   └─── README.md
logs
```

dbt team strongly recommends using version control (git), for that reason `dbt init` command automatically generates `.gitignore` file.
Also pay attention to `dbt_project.yml` file, it is the main configuration file.

`dbt_project.yml` file contains below (automatically generated) config options:

```yaml
# Name our project! Project names should contain only lowercase characters
# and underscores. A good package name should reflect our organization's
# name or the intended use of these models
name: 'dbt_databricks_demo'
version: '1.0.0'

# This setting configures which "profile" dbt uses for this project.
profile: 'dbt_databricks_demo'

# These configurations specify where dbt should look for different types of files.
# The `model-paths` config, for example, states that models in this project can be
# found in the "models/" directory. we probably won't need to change these!
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:         # directories to be removed by `dbt clean`
  - "target"
  - "dbt_packages"

# Configuring models
# Full documentation: https://docs.getdbt.com/docs/configuring-models

# In this example config, we tell dbt to build all models in the example/
# directory as views. These settings can be overridden in the individual model
# files using the `{{ config(...) }}` macro.
models:
  dbt_databricks_demo:
    # Config indicated by + and applies to all files under models/example/
    example:
      +materialized: view
```

Using this file, among other things, dbt knows where to find models, macros, tests, and docs.

### Profiles file

During the initialization process (`dbt init` and subsequent prompts), dbt creates and populates `profiles.yml` file.

Example:

`~/.dbt/profiles.yml`

```yaml
dbt_databricks_demo:
  outputs:
    dev:
      catalog: dbt-core-demo-catalog
      host: xxxxxxxxx.cloud.databricks.com
      http_path: /sql/1.0/warehouses/xxxxxxxx
      schema: dbt-core-demo-schema
      threads: 1
      token: dapid121xxxxxxxxxxxxxxxxxxxxxxxxx
      type: databricks
  target: dev
```

If dbt fails to create this file, or simply we want to create this file manually, we can do so.

Basically, we should keep all the connection details to our data platform in `profiles.yml` file. We can keep it in either `~/.dbt/` directory, or in the dbt project directory (next to `dbt_project.yml` file).

`profiles.yml` file

```yaml
dbt_databricks_demo: # <= this name should be the same as the profile name in dbt_project.yml file
  outputs: # available targets (data platforms and databases)
    dev:
      type: databricks
      catalog: dbt-core-demo-catalog
      schema: dbt-core-demo-schema  # Required
      host: yourORG.databrickshost.com # Required
      http_path: /SQL/Our/HTTP/PATH # Required
      token: dapiXXXXXXXXXXXXXXXXXXXXXXX # Required Personal Access Token (PAT) if using token-based authentication
      threads: 1  # Optional, default 1
      connect_retries: 3 # Optional, default 1

    stage:  # additional stage target
      type: databricks
      host: stage.db.example.com
      user: John_Smith
      password: <stage_password>
      port: 5432
      dbname: my_stage_db
      schema: analytics
      threads: 1

    prod:  # additional prod target
      type: databricks
      host: prod.db.example.com
      user: John_Doe
      password: <prod_password>
      port: 5432
      dbname: my_prod_db
      schema: sales
      threads: 1

  target: dev # target name that is chosen as default
```

`outputs` key defines all the available target environments. The `target` key defines
which of the output environments to be used as a default *target* environment.
In this example `dev` target is the default target. When we run dbt commands such as `dbt run`, it uses this `dev` target.

If we have more than one target and want to use target other than default in the command line without modifying `profiles.yml` file, we can do so by specifying it using `--target` option.

```bash
dbt run --target prod
```

Note: if the database schema does not exist, dbt will add a code to create the schema.

To avoid hard coding credentials, we can use environment variables using [`env_var(<VARIABLE_NAME>, default_value)` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var).

`profiles.yml`

```yml
profile:
  target: dev
  outputs:
    prod:
      type: databricks
      host: 127.0.0.1
      catalog: dbt-core-demo-catalog
      schema: dbt-core-demo-schema  # Required
      # IMPORTANT: Make sure to quote the entire Jinja string here
      user: "{{ env_var('USER_NAME') }}"
      password: "{{ env_var('PSWRD') }}"
      ....
```

#### Using target value

`profiles.yml` file has [`target` keyword](https://docs.getdbt.com/reference/dbt-jinja-functions/target) and its value is the chosen/target environment where models will be materialized.

Using the `profiles.yml`, dbt provides us with a `target` object. This object has below fields:

- target.profile_name
- target.name
- target.schema
- target.type *(One of "postgres", "snowflake", "bigquery", "redshift", "databricks")*
- target.threads
- ... (data platform specific values)

We can use this `target` object in our models or `properties.yml` files.

1. using `target` object in model:

    `models/customers.sql`

    ```sql
    select
      ...
      {% if target.type == 'redshift' %}
        ISNULL(employee_middle_name, "")
      {% elif target.type == 'snowflake' %}
        IFNULL(employee_middle_name, "")
      {% endif %}
    from source('web_events', 'customers')
    ```

  Switching between `ISNULL` and `IFNULL` based on the data platform.

1. using target in `*.yml` file:

  `models/sources.yml`

  ```yml
  version: 2
  sources:
    - name: sources
      database: |
        {%- if target.name == "dev" -%} raw_dev
        {%- elif target.name == "stage"  -%} raw_stage
        {%- elif target.name == "prod"  -%} raw_prod
        {%- endif -%}
      schema: raw_data
      tables:
        - name: sales
        - name: marketing
      ...
  ```

  Based on the target, the database to be used is dynamically selected.

### Config

We can configure our dbt project using

1. `config()` macro
1. `*.yml` files
1. `dbt_project.yml` file

#### Model Configuration

We can [configure models](https://docs.getdbt.com/docs/build/sql-models#configuring-models) by setting aliases to tables and views, specifying materialization and more.

Since `config()` macro is embedded onto model files directly, it can configure only one model.
`*.yml` files can configure both single and multiple models, but each model's name must be defined.
`dbt_project.yml` file can configure  both single and multiple models. Also, folder path can be used.

- `dbt_project.yml`

    ```yaml
    models:
      my_dbt_project:
        sub_folder_A: # below configuration affects all the models within this sub_folder
          +materialized: table
          +schema: schema_name
          +sql_header: <string>
          run_after: sql_statement
    ```

- `models/properties.yml`

    ```yml
    version: 2

    models:
      - name: model_1
        config:
          materialized: table
          schema: insights
          columns:
            - id
            - name

      - name: model_2
        config:
          materialized: table
          columns:
            - id
            - name
    ```

    Note: We can have multiple `*.yml` files and we can name them anything we want.

`models/my_simple_model.sql`

```sql
{{
  config(
    materialized="table",
    schema="sales",
    alias="transformed_orders",
    tags=["order", "inventory"]
    )
}}

select
  ...
from orders
```

#### Schema Concatanation

In the `profiles.yml` file schema has to be defined. It is considered a default schema.

`profiles.yml`

```yaml
profile:
  target: dev
  outputs:
    prod:
      type: databricks
      catalog: production
      schema: year2025
      ....
```

When you define a schema in `dbt_project.yml`, `*.yml` files or using `config()` macro, the schema name you defined will be [concatinated](https://docs.getdbt.com/docs/build/custom-schemas) with the default schema name.

For example

`models/orders.sql`

```sql
{{
  config(
    materialized="table",
    schema="sales"
    )
}}

select
  ...
from orders
```

dbt will create this table in `year2025_sales` schema (if schema does not exist, dbt creates the schema first).
I repeat dbt will create `production.year2025_sales.orders` table, not `production.year2025_sales.orders` table.

It is possible to override this behaviour using [generate_schema_name arguments](https://docs.getdbt.com/docs/build/custom-schemas#changing-the-way-dbt-generates-a-schema-name) macro.

##### Incremental models materialization

If we want to materialize our model as a table, and reflect changes on the base table without rebuilding our model, we can use  [*incremental* models](https://docs.getdbt.com/docs/build/incremental-models). Incremental models especially useful when the base table is large and rebuilding the model takes a lot of resources.

When the incremental model is run for the first time, it will create the target table and transforms & inserts the data into the newly created target table. In the subsequent runs, it will only insert new data (filtered via where logic) into the target table. In simple words, in the first run dbt parses the incremental models as `create table` statement, in the subsequent runs as `insert into` statement.

To configure the model as incremental, we need to

1. set `materialized` option to `incremental`
2. use `is_incremental()` macro to filter new data

Let's say we have a `sales.sql` model that drives its data from `raw_orders_data` source.

`models/sales.sql`

```sql
{{config(materialized='incremental')}}

select
  id,
  order,
  time,
  destination
from {{ source('sales', 'raw_orders_data')}}
where order_status = 'fulfilled'
{% if is_incremental() %}
  and
  time > (select max(time) from {{ this }} )
{%endif %}
```

`is_incremental()` macro returns `true` if the target table already exists and `materialized` option is set to `incremental`. Also notice the usage of `{{ this }}` to refer to the model.

In the first run, above code will be compiled into

```sql
select
  id,
  order,
  time,
  destination
from <database>.<schema>raw_orders_data
where order_status = 'fulfilled';
```

In the subsequent runs:

```sql
select
  id,
  order,
  time,
  destination
from <database>.<schema>raw_orders_data
where order_status = 'fulfilled'
and
time > (select max(time) from <database>.<schema>raw_orders_data )
;
```

Note: this is an append-only behavior. It only appends new rows. As for syncing updated/modified rows we need to define [`unique_key`](https://docs.getdbt.com/docs/build/incremental-models#defining-a-unique-key-optional) parameter. `unique_key` parameter accepts both a string and a list.

In our example the `id` column is unique. We can use this column to determine newly added and modified records.

`models/sales.sql`

```sql
{{config(
  materialized='incremental',
  unique_key='id'
  )}}

select
...
```

If we need to create the target table again instead of update it, we should use `--full-refresh` option with `dbt run` command.

```bash
dbt run --full-refresh --select sales+
```

`+` at the end of the model name tells dbt to rebuild any downstream models as well.

#### Setting aliases

1. `dbt_project.yml`

    ```yaml
    models:
      my_dbt_project:
        inventory: # model name within the dbt project
          +alias: transformed_inventory_data # the table/view name that will be created in database
    ```

1. `models/properties.yml`

    ```yaml
    version: 2

    models:
      - name: inventory # model name within the dbt project
        config:
          alias: transformed_inventory_data # the table/view name that will be created in database
    ```

1. `config()` macro

    `models/inventory.sql`

    ```sql
    {{ config(
        alias="sales_dashboard",
        materialized='table'
    )}}

    select
    ...
    from raw_inventory
    ```

### Plus (+) sign

Let's consider the following case: in our project we have folders, models or other files that have the same name as dbt configuration keys, for example, `models/tags` folder, or `models/target.sql` model. In our `dbt_project.yml` file, when we specify configurations such such as adding tags, dbt might have hard time distinguishing between config instructions and resource (folder, file) names.

To distinguish resource name from configs, it is recommended to prefix the config keys with the plus, (+), sign. We can prefix any config in the `dbt_project.yml` file with the plus sign (even if there is no name clash/ambiguity).

`dbt_project.yml`

```yaml
models:
  my_dbt_project:
    inventory: # model name within the dbt project
      +alias: transformed_inventory_data # the table/view name that will be created in database
```

Use plus sign only with `dbt_project.yml` file.

### Parsing and Compiling

We can find the Jinja parsed version of our models in `target/compiled/<project_name>/models/` folder.

We can find the compiled (final) version of our models in `target/run/<project_name>/models` folder.

### Commands

dbt core is command line tool. We can get the summary of available commands by running `dbt --help` command. There are many options/flags as well to be used with the commands.

**dbt run:**

- `dbt run`: compile and execute all models
- `dbt run --select my_model_name`: compile and execute specific model
- `dbt run -s my_model_name"`: compile and execute specific model
- `dbt run --select sub_folder`: compile and execute all models in a specific sub-folder
- `dbt run --exclude my_model`: compile and execute all the models except for a specific model
- `dbt run --exclude sub_folder`: compile and execute all the models except for models inside specific sub-folder

Note: `dbt compile` command parses the models but does not execute them (does not send them to the platform). `dbt run` command parses the models and executes them (sends them to the platform to be executed).

**dbt ls:**

Sometimes, especially when we use `--exclude` option, it is difficult to know which resources we will run. We can use `dbt ls` command to check a list of the resources that would be executed.

```bash
dbt ls --exclude sub_folder"
```

## dbt Fusion Engine

dbt team is developing new software, dbt Fusion engine. It is written in Rust and still in beta (development) mode. (dbt core is written in python.) dbt Fusion engine is going to be much faster than dbt core. It will do all the things dbt core does plus much more, such as catch incorrect SQL in dbt models, and preview inline CTEs.

Fusion engine contains mixture of source-available, proprietary, and open source code.
It is something you can keep an eye on and once it comes out of beta, you may consider using.

## Other features

dbt has many more features such as tags, [exposures](https://docs.getdbt.com/docs/build/exposures), [groups](https://docs.getdbt.com/docs/build/groups), contracts and more. They didn't seem essential to me, so I didn't include them in this tutorial.

## Best Practices

dbt labs team recommends below best practices:

1. Use version control system such as git.
1. Use separate production and development environments through the use of targets within a profile file.
1. Use environment variables to load sensitive credentials using [`env_var` function](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var). It can be used anywhere that jinja can be used.
1. Group your models in directories within your `models/` directory

You can learn more about recommended best practices [on this page](https://docs.getdbt.com/best-practices/best-practice-workflows#best-practice-workflows).

## Links

- [What is dbt](https://docs.getdbt.com/docs/introduction#the-power-of-dbt)
- [GitLab using dbt with Snowflake](https://gitlab.com/gitlab-data/analytics/-/tree/master/transform/snowflake-dbt)
- [dbt-utils](https://github.com/dbt-labs/dbt-utils): Utility functions for dbt projects.
