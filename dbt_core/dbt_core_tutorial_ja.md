# dbt Core 徹底解説

dbtはデータビルドツールの略です。[dbt core](https://github.com/dbt-labs/dbt-core)は、データ変換を目的としたCLIツールです。
これはPythonで書かれたオープンソースツールです。

(クラウドホスト型（有料）のdbt cloudも提供されています。)

dbt core は SQL クライアントと考えることができます。データ変換プロセスの実行と管理を容易にする機能を備えています。
dbt core を使用するとテーブルとビューを作成できますが、テーブルの削除は**できません**。

dbt core についてさらに詳しく説明する前に、まずデータ変換とは何かを明確にしておきましょう。
あなたがデータエンジニアとして企業で働いていると想像してみてください。あなたの企業は、API、顧客、サプライヤー、社内システムなどからデータを取得しています。
データは新たな宝庫であるため、このデータは企業の業務に関する洞察を得るのに役立つ可能性があることはご存知でしょう。
そこで、最初のステップとして、利用可能なすべてのデータを抽出し、**表形式**でデータウェアハウス（Snowflake、DataBricks、BigQuery など）にロードします。
このデータは、変更や変換をせずにそのまま保存するため、**生データ**と呼ばれます。

営業／マーケティング／ビジネス分析チームがこのデータを使用して企業の業務に関するビジネス洞察を得たい場合、不要なデータを除外したり、データを変更したり、データの形式を変更したりするために、複雑なクエリを作成する必要があります。
彼らはデータエンジニアではないため、複雑な SQL クエリの作成は得意ではありません。
同僚の作業を楽にするために、次のステップとして、生データを新しいビューまたはテーブルに分類されたデータに変換します。これには、データの特定の部分をフィルタリング、変更、またはフォーマットすることが含まれます。この変換は、行のフィルタリング、行のグループ化、列名の変更、既存の値に基づく新しい値の計算などによって実現できます。

dbt core は、この変換ステップを支援します。
dbt は、コードとコードファイルを整理するのに役立ち、SQL では利用できない追加機能も提供します。

つまりは：

- dbt は、Snowflake、Databricks などのデータプラットフォームに既にロードされているデータを操作します。
- この生データは構造化された形式（通常はテーブル）である必要があります。
- 変換コードは、SQL と Jinja を使用して構造化された形式で記述します。
- dbt コアがコードを解析およびコンパイルし、データプラットフォームに送信します。
- データプラットフォームがコードを実行します（新しいテーブルとビューを作成します）。

## 主な概念と機能

- models
- jinja
- macros
- hooks
- tests
- docs
- analysis

> 注: dbt は、Snowflake、Databricks などのデータウェアハウスに既にロードされているデータを操作します。この生データは、通常はテーブルなどの構造化形式である必要があります。

- dbt では `Select` ステートメントのみを記述し、dbt は `select` ステートメントを `create` 定型コードでラップします。
- SQL ステートメントは、選択したプラットフォームと互換性のある SQL 方言を使用して記述する必要があります。Snowflake を使用している場合は、Snowflake 互換の SQL を使用する必要があります。
- Jinja は、構成ファイルや SQL ステートメントを含め、dbt プロジェクトで幅広く使用できます。

### モデル

`select` 文を含み、実行を目的とした SQL ファイルは [**model**](https://docs.getdbt.com/docs/build/sql-models) と呼ばれます。
dbt は `select` 文を `create` 定型コードでラップします。

> 注: モデルファイルは `models` フォルダに配置する必要があります。

以下の列を持つ `raw_sales_data` という名前の生のテーブルがあるとします。

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

`raw_sales_data` テーブルのデータを変換します (「simple_sales_data」という新しいビューを作成します)。

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

dbt はコードを解析して以下のコードにコンパイルします。

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
  )
```

dbt は、プラットフォーム固有の `create` 定型コードでコードをラップします。

モデル名はモデルファイル名から派生し、ビュー/テーブルを作成します。簡単に言うと、作成されるビュー/テーブルの名前はモデルファイル名に基づいて決定されます。モデル名は大文字と小文字が区別されます。

モデルファイルは、`models` フォルダ内のサブディレクトリに配置できます。

### Materialization

dbt はデフォルトでビューを作成します。ビューではなくテーブルを作成したい場合もあります。モデルからデータベースオブジェクト（ビュー、テーブルなど）を作成することをマテリアライゼーションと呼びます。

利用可能なマテリアライゼーションオプション：

- view (default)
- table
- incremental
- ephemeral
- materialized_view

**Incremental**
: [incremental models](https://docs.getdbt.com/docs/build/incremental-models) は、生データテーブルから既存のターゲット（変換）テーブルに新しいレコードを挿入します。このオプションは、モデルが最後に実行された日時を追跡するために、ターゲットテーブルに新しい列を追加します。この情報に基づいて、ソーステーブルのデータからターゲットテーブルに挿入するレコードを決定します。増分モデルの設定には追加の構成が必要です。
: dbt の実行に時間がかかりすぎる場合は、このオプションを使用します。

**Ephemeral**
: エフェメラルモデルは解析され、共通テーブル式（CTE）にコンパイルされます。
つまり、エフェメラルモデルはデータプラットフォーム上に作成されません。
エフェメラルモデルは、他の（依存する）モデルと組み合わせて使用することを目的としています。
: エフェメラルモデルは、プロジェクトのモジュール化と再利用性を維持するのに役立ちます。ただし、いくつかの制限事項があります。

上記に加えて、データプラットフォームによっては追加のマテリアライゼーションオプションが使用できる場合があります。詳しくは、各プラットフォームのドキュメントをご確認ください。

> 注: dbt core ではテーブルやビューを削除できません。データベースプラットフォームで手動で削除する必要があります。

### Jinja

モデルには[jinja](https://jinja.palletsprojects.com/en/stable/)構文を含めることができます。Jinjaは繰り返しのコードブロックなどにも役立ちます。

`models/US_Customer_Orders.sql`

```sql
Select
    {% for customer_number in range(1, 6) %}
        cust_{{customer_number}} as USA_Customer{{customer_number}},
        cust_{{customer_number}}_ord as USA_Customer{{customer_number}}_order
    {% if not loop.last %},{% endif %}
    {% endfor %}
from customers
where country = 'USA'
```

上記のコードは解析され、以下のコードにコンパイルされ、データ プラットフォームに送信されます。

```sql
create or replace view <db_name>.<schema_name>.US_Customer_Orders
  as (
    Select
        cust_1 as USA_Customer1,
        cust_1_ord as  USA_Customer1_order,

        cust_2 as USA_Customer2,
        cust_2_ord as  USA_Customer2_order,

        cust_3 as USA_Customer3,
        cust_3_ord as  USA_Customer3_order,

        cust_4 as USA_Customer4,
        cust_4_ord as  USA_Customer4_order,

        cust_5 as USA_Customer5,
        cust_5_ord as  USA_Customer5_order

    from customers
    where country = 'USA'
    )
```

dbt はコードを解析して SQL (`create`) ステートメントにコンパイルし、データ プラットフォーム (Snowflake、DataBricks など) に送信して実行します。

### Configuration

dbt は 3 つのレベルで設定できます。

1. `dbt_project.yml` ファイル: プロジェクト全体の設定
1. モデルファイル内の `config()` Jinja 関数: モデル固有の設定
1. `*.yml` ファイル (`models/properties.yml` または `sources/properties.yml` など)

dbt は、設定のために `dbt_project.yml` ファイルとモデルファイルの `config` セクションをチェックするだけでなく、プロジェクト全体で `.yml` ファイルも検索します。
これらの `.yml` ファイルの名前は任意です。このチュートリアルでは `properties.yml` という名前を使用します。
これらのファイルは、対象となるモデルと同じフォルダ/サブフォルダに配置されます。
dbt は、これらの `.yml` ファイルの内容と `dbt_project.yml` および `config` 関数を解析し、以下の優先順位で設定を適用します。

1. モデルファイル内の `config()` Jinja 関数
2. `.yml` 設定ファイル
3. `dbt_project.yml` ファイル

### Jinja Functions

dbt は Jinja と強力に統合されています。Jinja は dbt プロジェクトのほぼすべての場所（テスト、モデル、設定ファイル、ドキュメントなど）で使用できます。
dbt チームは、`docs block`、`snapshots`、`logs` など、dbt 固有の関数を追加することで Jinja を拡張しました。
[dbt 固有の Jinja 関数](https://docs.getdbt.com/reference/dbt-jinja-functions) の全リストをご覧ください。

いくつかの dbt 機能は Jinja のおかげで実現しました。

#### Ref()

[`ref()` 関数](https://docs.getdbt.com/reference/dbt-jinja-functions/ref) を使用すると、テーブルやビューを参照するのと同じようにモデルを参照できます。
`ref(model_name)` は一意の名前で動作します。モデル名が重複しないように注意してください。

`models/customers.sql`

```sql
select
  id as customer_id,
  name
from raw_customer_data
```

以下の `orders` モデルでは `customers` モデルを参照します。

`models/orders.sql`

```sql
Select
  id as order_id,
  order_date,
  customer.name as customer_name
from raw_order_data
inner join {{ ref('customers') }} as customer
using(customer_id)
```

dbt は `{{ ref('customers') }}` を正しい `<dbt_name>.<schema_name>.customers` ビュー/テーブル名に置き換えます。
データプラットフォーム上に `customers` ビュー/テーブルが作成されます。その後、 `orders` ビュー/テーブルが作成されます。

#### Sources()

データベース、スキーマ、テーブル名をハードコーディングする代わりに、それらすべてを yaml ファイルで定義し、[`source()` 関数](https://docs.getdbt.com/reference/dbt-jinja-functions/source) を使用してモデル ファイルで参照することができます。

```python
source('source_name', 'table_name')
```

ソースは yaml ファイルで定義され、この yaml ファイルは `models` フォルダー内の任意の場所に配置できます。

`models/sources.yml`

```yaml
version: 2

sources:
  - name: sales_prod # ソース名
    database: PROD_SALES_DB
    schema: RAW_SALES
    tables:
      - name: accounts
      - name: opportunities

    - name: sales_contracts # ソース名
      database: Sales_contracts
      schema: contracts
      tables:
        - name: orders
        - name: shipments

  - name: sales_archive # ソース名
    database: ARCHIVE_SALES_DB
    schema: RAW_SALES
    tables:
      - name: accounts
      - name: opportunities
```

モデルファイル内のソースを参照してください:

`models/orders/order_by_customers.sql`

```sql
select
  ...
from {{ source('sales_archive', 'accounts') }}
```

dbt は上記の情報を使用して完全修飾テーブル参照を構築します。

以下の SQL にコンパイルされます。

```sql
select
  ...
from ARCHIVE_SALES_DB.RAW_SALES.accounts
```

データ プラットフォームでテーブルの場所が変更された場合 (データベース名やスキーマ名の変更など)、この yaml ファイルを変更するだけで済み、モデル ファイルを変更する必要はありません。

#### Macros

マクロは関数に少し似ています。マクロは引数を取り、値を返すことができます。戻り値は複数行のコードになる場合があります。

マクロは `{% macro %}` ブロックで始まります。マクロは `macros` フォルダ内の `.sql` ファイルで定義されます。

構文：

```jinja
{% macro macro_name(argument1, argument2 ...) %}
    return_value
{% endmacro %}
```

マクロ呼び出しはマクロの戻り値に置き換えられます。

例:

`macros/fix_string.sql`

```sql
{% macro fix_string(column_name) %}
    upper(trim(coalesce(column_name, ''))) as column_name
{% endmacro %}
```

上記のマクロを呼び出す:

`models/sales_by_department.sql`

```sql
select
  id as user_id,
  {{ fix_string(username) }},
  {{ fix_string(department) }}
  ...
from sales_data
```

コンパイルされたSQLは

```sql
select
  id as user_id,
  upper(trim(coalesce(username, ''))) as username,
  upper(trim(coalesce(department, '')))  as department
  ...
from sales_data
```

##### config()

モデルでは `config` マクロを使用できます。他の設定と同様に、このマクロを使ってモデルの実体化方法を設定できます。

```sql
{{ config(materialized='table') }}

select
    id as user_id
    ...
from customers
```

dbtには600以上の組み込みマクロがあります。さらに、[dbt-utils](https://github.com/dbt-labs/dbt-utils)などのパッケージでは、さらに多くのマクロが利用可能です。

##### Hooks

各モデルの実行前または実行後に特定のコードを実行する必要がある場合は、[フック](https://docs.getdbt.com/docs/build/hooks-operations) を使用できます。フックとは、各モデルの開始時または終了時、あるいは各 `dbt run` コマンドの開始時または終了時に実行される SQL スニペットです。

[pre-hook と post-hook](https://docs.getdbt.com/reference/resource-configs/pre-hook-post-hook): 各モデルの開始時または終了時に実行されます。
[on-run-start と on-run-end](https://docs.getdbt.com/reference/project-configs/on-run-start-on-run-end): 各 `dbt run`/`dbt test`/`dbt docs generate` などのコマンドの開始時または終了時に実行されます。

フックは、単一の SQL 文または複数の SQL 文の **リスト** として記述できます。

構文:

`dbt_project.yml`

```yaml
models:
  my_dbt_demo:
    # 各 `dbt run`/`dbt test`/`dbt docs generate` コマンドの前後に実行されます。
    on-run-start: SQL文 |  [SQL文, SQL文, ...]
    on-run-end: SQL文 |  [SQL文, SQL文, ...]

    # 各モデルの実行の前後に実行されます
    additional_permission_needed_models:
      +pre-hook: SQL文 | [SQL文, SQL文, ...]
      +post-hook: SQL文 | [SQL文, SQL文, ...]
```

`models/<model_name>.sql`

```sql
{{ config(
    pre_hook="SQL文" | [SQL文, SQL文, ...],
    post_hook="SQL文" | [SQL文, SQL文, ...],
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
      pre_hook: SQL文 | [SQL文, SQL文]
      post_hook: SQL文 | [SQL文, SQL文]
```

例:

```yaml
models:
  my_dbt_demo:
    # 各モデルの実行の前後に実行されます
    additional_permission_needed_models:
      +pre-hook: "grant usage on schema {{ target.schema }} to role env_var('PROD_USER');"
```

フック内でマクロを呼び出すこともできます。

注: フックは累積的に適用されます。dbt_project.yml とモデルの設定ブロックの両方でフックを定義した場合、両方のフックセットがモデルに適用されます。

##### Var()

`dbt_project.yml` ファイルからモデルに変数を渡すことが可能です。

プロジェクト内で変数を定義するには、`dbt_project.yml` ファイルに `vars` キーワードを追加する必要があります。

`dbt_project.yml`

```yaml
name: dbt_2025_project
config-version: 2

# いくつかの設定
...

# 変数:
# キー:値
vars:
  focus_customer_email_category: feedback
  year_end_month: 03
```

モデルでの変数の使用

`models/customer_voice.sql`

```sql
select
  *
from contact_emails
where category = '{{ var("focus_customer_email_category") }}'
```

var() 関数は、オプションの 2 番目の引数をデフォルト値として受け取ります。

`models/customer_voice.sql`

```sql
select
  *
from contact_emails
where category = '{{ var("focus_customer_email_category", "complaint") }}'
```

##### Log()

モデルとマクロにログステートメントを記述できます。ログ（出力）ファイルは `logs` フォルダ内に保存されます。ログファイルには、ログ出力だけでなく、dbt が自動的に生成した出力も表示されます。

`models/inventory.sql`

```sql
{% log('hello world') %}

select
  ...
from inventory_data
```

### Tests

モデルをテストできます。[dbt テスト](https://docs.getdbt.com/docs/build/data-tests) は、SQL と Jinja で記述された `select` ステートメントです。

テストの使用方法:

1. モデル（変換ロジック）

    `models/marketing_budget.sql`

    ```sql
    select
        id as campaign_id,
        campaign_budget,
        campaign_cost
    from raw_marketing_data
    ```

    `campaign_budget` の合計は `campaign_cost` の合計よりも大きくなるはずです。

1. 特異テスト（特定のモデルを対象とする）

    `tests/marketing_budget_test.sql`

    ```sql
    with totals as
    (select
        sum(campaign_budget) as total_campaign_budget,
        sum(campaign_cost) as total_campaign_cost
    from marketing_budget -- モデル名
    )

    select *
    from totals
    where total_campaign_cost >  total_campaign_budget
    ```

    上記のクエリは、`total_campaign_cost` が `total_campaign_budget` よりも高い場合、つまりマーケティング予算が超過した場合にのみ行を返します。
    dbt はこのテストを実行し、行が返されない場合は成功を示し、テスト クエリが行を返す場合は失敗を示します。

注意: テストクエリにはセミコロンを追加しないでください。

特定のモデルを対象とするテストは、特異テストと呼ばれます。テストファイルは `tests` フォルダ内に配置します。

まとめると、dbt テストは、モデルが持つべきではないレコードを取得しようとする SQL クエリ（SELECT ステートメント）です。
`dbt test` コマンドは、`tests` フォルダ内のすべての特異テストファイルを **自動的に** 実行します。

#### Generic Data Tests

単一テストは特定のモデルのみを対象とします。
汎用テストも使用できます。汎用データテストは何度でも再利用できます。

dbt は以下の汎用テストを標準で提供しています。

- `unique`
- `not_null`
- `accepted_values`
- `relationships`

必要なのは、モデル（および特定の列）に対してこれらのテストを実行することを指定することです。
これは、`models` フォルダ内の `.yml` ファイルを使用して行います。

`models/properties.yml`

```yaml
version: 2

models:
  - name: events # イベント モデル (ビュー/テーブル)
    columns:
      - name: event_id
        data_tests:
          - unique
          - not_null
      - name: status
        data_tests:
          - accepted_values:
              values: ['held', 'pending', 'waiting for approval']
      - name: venue
        data_tests:
          - not_null
          - relationships:
              to: ref('venues')
              field: venue_id

  - name: venues # venues モデル (ビュー/テーブル)
    columns:
      - name: venue_id
        data_tests:
          - unique
          - not_null
```

上記のファイルには、「venues」と「events」という2つのモデルのテストが含まれています。
テスト内容は次のとおりです。

1. `events.event_id` 列と `venues.venue_id` 列は一意であり、null ではありません。
1. `events.status` 列には、「held」、「pending」、「waiting for approval」のいずれか1つの値のみが含まれています。
1. `events.venue` 列は null ではなく、`venues.venue_id` 列から有効な値を参照しています（外部キーテスト）。

上記のテストを実行するには、「dbt test」コマンドを実行します。
dbt はすべてのテストを実行し、成功したテストの数と失敗したテストの数を表示します。

(テスト内のSELECT文がレコードを返した場合、テストケースは失敗とみなされます。SELECT文がレコードを返さなかった場合、テストケースは成功とみなされます。)

上記の4つの汎用テストに加えて、[dbt-utils](https://github.com/dbt-labs/dbt-utils?#generic-tests) などのパッケージにも他のテストがあります。

#### Generic testsの作成

独自の汎用テストを作成することもできます。すべての汎用テストは、標準引数（model と column_name）のいずれか、または両方を受け入れる必要があります。

model: モデル名。モデルはビューまたはテーブルにマテリアライズされ、これらのマテリアライズされた（変換された）ビュー/テーブルをテストします。

column_name: テストが列レベルで実行される場合は、当然列名も必要です。

たとえば、列の値が正かどうかをテストする汎用テストを作成するには、以下のように `test` ブロックを使用します。

`tests/positive.sql`

```sql
{% test positive(model, column_name) %}
    select
        {{ column_name }}
    from {{model}}
    where {{ column_name }} < 0
{% endtest %}
```

モデルをテストするには、モデルに含まれないはずのレコードをクエリします。

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

テストは解析され、以下のクエリにコンパイルされます。

```sql
select
      age
from <dbt_name>.<schema_name>.employees
where age < 0
```

三つ以上の引数を受け入れる汎用テストを作成する場合は、[このドキュメント](https://docs.getdbt.com/best-practices/writing-custom-generic-tests) を確認してください。

### Docs

dbt は、モデル、テスト、設定ファイルに基づいてドキュメント（docs）を生成できます。
より包括的なドキュメントを生成するために説明を追加すると、dbt はこれらの説明を生成されたドキュメントに組み込みます。
dbt はドキュメントを表示するための静的 Web サイトを生成します。

properties.yml ファイル内に説明を追加できます。

`models/properties.yml`

```yml
version: 2

models:
  - name: events
    description: この表にはマーケティングキャンペーンイベントが含まれている
    columns:
      - name: event_id
        description: イベントの一意の識別子（列）
        data_tests:
          - unique
          - not_null
          - positive:
            description: カスタムテスト
        ...

  - name: stuff
    description: 会社の全従業員
    columns:
      - name: id
        description: 会社で働く従業員ID
        data_tests:
          - not_null
```

モデル、列、汎用テストなどについて説明を記述できます。

個別のテストについても説明を記述できます。

`tests/join_leave_test.sql`

```yaml
version: 2
data_tests:
  - name: join_leave_test
    description: このテストは、すべての「退社」日が「入社」日よりも大きいことを確認する。
```

doc ファイルと呼ばれる `.md` ファイルを使用して、より長い説明を記述することもできます。
doc ファイルには `{% docs %}` jinja ブロックを含める必要があり、markdown コードを含めることができます。

`docs/events.md`

```jinja
{% docs campaign_events %}

# キャンペーンイベント

**以下の都市でマーケティングキャンペーンイベントが開催されます**

- ロンドン（英国）
- 東京（日本）

{% enddocs %}
```

上記のドキュメントを `models/properties.yml` ファイルに含めます。

```yaml
version: 2

models:
  - name: events
    description: '{{ docs("campaign_events") }}'
    columns:
      - name: event_id
        description: イベントの一意の識別子
        data_tests:
          - unique
          - not_null
        ...
```

ドキュメントを生成するには、`dbt docs generate` コマンドを実行する必要があります。

デフォルトでは、dbt はすべてのリソースパスからドキュメントを検索します。技術的には、ドキュメントファイルを `docs` フォルダ内に保存する必要はありません。ドキュメントファイルを、それらが記述するモデルの近くに置いても構いません。

すべてのドキュメントファイルを `docs` フォルダ内にのみ保存したい場合は、`dbt_projects.yml` ファイルでそのように指定します。
指定すると、dbt はドキュメントを `docs` フォルダ内でのみ検索するようになります。

`dbt_project.yml`

```yml
# いくつかの設定
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
macro-paths: ["macros"]
# その他のパス ...
docs-paths: ["docs"]
# もう設定...
```

- `dbt docs generate` コマンドを実行して静的サイトを生成します
- `dbt docs serve` コマンドを実行してブラウザで静的サイトを確認します

### Seeds

dbt はデータのロードではなく、変換に使用されます。ただし、dbt のコア機能ではないにもかかわらず、データのロードは可能です。

dbt は csv ファイルを「seeds」と呼びます。
「dbt seed」コマンドは、シードファイル名と同じ名前の新しいテーブルを作成し、csv ファイルのデータをデータプラットフォームにロードします。

`seeds/capitals.csv`

```csv
Country, Capital
日本、東京
フランス、パリ
中国、北京
...
```

dbtはCSVファイルのデータに基づいて各列のデータ型を推測します。`seeds/properties.yml`ファイルで列のデータ型を指定することもできます。

`seeds/properties.yml`

```yaml
version: 2

seeds:
  - name: capitals
    config:
      column_types:
        - Country: VARCHAR(32)
        - Capital: VARCHAR(32)
      delimiter: ","
```

`dbt seed` コマンドを実行すると、データプラットフォームに `capitals` という新しいテーブルが作成されます。
その後、モデル内の `ref` 関数を使用してこのテーブルを参照できるようになります。

注: csv ファイルの読み込みは dbt の主要機能ではありません。dbt は小さな csv ファイルの読み込みにのみ使用してください。

### Analysis ファイル

モデルを作成するだけで実行しない場合は、これらのファイルを `Analysis` フォルダに保存する必要があります。
dbt はこれらの [分析ファイル](https://docs.getdbt.com/docs/build/analyses) をコンパイルしますが、実行は行いません。

コンパイル済みのファイルは `target/compiled` フォルダ内にあります。

`analyses/order_accounts.sql`

```sql
  select
    {{ macro_name(column) }}
    ...
  from {{ ref('some_model_name') }}
```

### Packages

dbt には多くの機能が標準で用意されています。しかし、[パッケージ](https://hub.getdbt.com/) を使用することで、dbt のテストおよびマクロユーティリティをさらに拡張できます。

以下に、人気の dbt パッケージをいくつかご紹介します。

- [dbt プロジェクトエバリュエーター](https://hub.getdbt.com/dbt-labs/dbt_project_evaluator/latest/): dbt プロジェクトにおいて、dbt Labs のベストプラクティスに合致していない領域をハイライト表示します。
- [dbt-utils](https://github.com/dbt-labs/dbt-utils): dbt ユーティリティ関数 (テストおよびマクロ)

上記のパッケージはどちらも dbt-labs によって作成されています。

その他のパッケージは、[パッケージハブ](https://hub.getdbt.com/) でご覧いただけます。

#### パッケージの追加方法

dbt プロジェクトフォルダ内に、`dependencies.yml` または `packages.yml` ファイルを作成します。
これは `dbt_project.yml` ファイルと同じ場所に配置する必要があります。

`dependencies.yml` または `packages.yml` ファイル内で、インストールするパッケージを指定します。

`packages.yml`

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.3.0
```

`dbt deps` コマンドを実行してパッケージをインストールします。

> dbt-utils パッケージには、次のようなユーティリティが含まれています。
> 結合された 2 つのテーブル/ビューの行数が同じであることを確認する `equal_rowcount` テスト
> ソースから重複行を削除するために必要な SQL コードを返す deduplicate マクロ。

### dbt 再実行

dbt は実行ごとにモデルをマテリアライズし続けます。これがまさに必要な動作になる場合もあります。

既にマテリアライズされているモデル/テーブル「customers」があるとします。
ベーステーブルの内容が変更されたので、モデル/テーブルの最新の変更を確認したいとします。
「dbt run」コマンドを実行します。

データプラットフォーム上に「customers」テーブルが既に存在するため、dbt はまず仮の名前で新しいテーブルを作成します。その後、1 回のトランザクションで「customers」テーブルを削除し、新しく作成されたテーブルの名前を「customers」に変更します。

---

## セットアップと設定

dbt coreは単なるCLIツールではなく、フレームワークです。つまり、コードを特定の方法で整理し、ファイルを特定のフォルダに構造化することが求められます。dbt coreは、このフォルダ構造の作成を支援します。

### インストール

dbt core は Python で書かれたオープンソースの CLI ツールです。dbt core をインストールする前に、Python (バージョン 3.7 以上) がインストールされていることを確認してください。
以下のパッケージをインストールする前に、Python 仮想環境を作成することをお勧めします。

dbt core のインストール:

```bash
pip install dbt-core

# 実行してインストールが正常に行われたか確認する
dbt --version

# 以下のような情報を返します
Core:
  - installed: 1.10.3
  - latest:    1.10.3 - Up to date!
...
```

#### Adapters

dbt core は SQL と Jinja コードを解析・コンパイルし、データプラットフォームに送信して実行します。
DataBricks データプラットフォームを使用します。

dbt core には以下のアダプターが必要です。

1. DataBricks 方言と互換性のある `create` SQL ステートメントでモデルをラップする
1. コンパイル済みのモデルを DataBricks データプラットフォームに接続/送信する

 [databricks アダプター](https://github.com/databricks/dbt-databricks)をインストール:

```bash
pip install dbt-databricks
```

### dbt コア プロジェクトのセットアップ

dbtプロジェクトを設定するには、以下のコマンドを実行します。

```bash
dbt init <project_name>
# dbt init dbt_databricks_demo

04:58:48  Running with dbt=1.10.3
04:58:48
Our new dbt project "dbt_databricks_demo" was created!

For more information on how to configure the profiles.yml file,
please consult the dbt documentation here:
  https://docs.getdbt.com/docs/configure-Our-profile

Happy modeling!
...
```

その後、プロフィールを設定するために、認証情報やその他の情報の入力を求められます。

例:

```bash
04:58:48  Setting up your profile.
Which database would we like to use?
[1] databricks

Enter a number: 1
# もうプロンプト
```

入力したデータを使用して、dbt は `~/.dbt` ディレクトリ内に `profiles.yml` ファイルを作成します。

また、現在のディレクトリに dbt_databricks_demo と logs という 2 つのフォルダを作成します。

フォルダ構造：

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
   └─── dbt_project.yml # <<---- 主なファイル
   └─── README.md
logs
```

dbt チームはバージョン管理 (git) の使用を強く推奨しています。そのため、`dbt init` コマンドは `.gitignore` ファイルを生成します。
`dbt_project.yml` ファイルはメインの構成ファイルです。

`dbt_project.yml` file

```yaml
# プロジェクトに名前を付けましょう！
# プロジェクト名は小文字とアンダースコアのみで構成してください。
# 適切なパッケージ名は、組織名やモデルの用途を反映したものであるべきです。
name: 'dbt_databricks_demo'
version: '1.0.0'

# この設定では、dbt がこのプロジェクトに使用する「プロファイル」を構成します。
profile: 'dbt_databricks_demo'

# これらの設定は、dbt がさまざまな種類のファイルを検索する場所を指定します。
# たとえば、`model-paths` 設定では、このプロジェクト内のモデルが
# "models/" ディレクトリにあることが指定されています。おそらくこれらを変更する必要はないでしょう。
model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:         # `dbt clean` コマンドで削除されるディレクトリ
  - "target"
  - "dbt_packages"


# モデルの設定
# 完全なドキュメント: https://docs.getdbt.com/docs/configuring-models

# このサンプル設定では、example/ ディレクトリ内のすべてのモデルをビューとしてビルドするように dbt に指示しています。
# これらの設定は、個々のモデルファイルで `{{ config(...) }}` マクロを使用して上書きできます。
models:
  dbt_databricks_demo:
    # + で示される設定は、models/example/ の下のすべてのファイルに適用されます。
    example:
      +materialized: view
```

このファイルを使用すると、dbt はモデル、マクロ、テスト、ドキュメントなどのファイルの場所を認識します。

### Profiles ファイル

初期化プロセス（`dbt init` およびそれに続くプロンプト）中に、dbt は `profiles.yml` を作成します。

その内容は以下のようになります。

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
      token: dapixxxxxxxxxxxxxxxxxxxxxxxxx
      type: databricks
  target: dev
```

dbt がこのファイルを作成できない場合、または手動で作成したい場合は、手動で作成できます。

基本的に、データプラットフォームへの接続情報はすべて `profiles.yml` ファイルに保存する必要があります。このファイルは `~/.dbt/` ディレクトリ、または dbt プロジェクトディレクトリ（`dbt_project.yml` ファイルの隣）に保存できます。

初期化時に、dbt は接続に `dev`（開発）環境という名前を付けます。

認証情報のハードコーディングを回避するために、`env_var(<VARIABLE_NAME>, default_value)` 関数を使用して環境変数を使用できます。

`outputs` キーは、利用可能なすべてのターゲット環境を定義します。`target` キー（`outputs` キーの前にある）は、どの出力環境をデフォルトの *target* 環境として使用するかを定義します。
この例では、`dev` ターゲットがデフォルトのターゲットです。dbt run などの dbt コマンドを実行すると、この `dev` ターゲットが使用されます。
複数のターゲットがあり、デフォルト以外のターゲットを使用したい場合は、`--target` オプションを使用してターゲットを指定できます。

```yaml
dbt_databricks_demo: # <= この名前はdbt_project.ymlファイルのプロファイル名と同じである必要があります。
  outputs: # 利用可能なターゲット
    dev:
      type: databricks
      catalog: dbt-core-demo-catalog
      schema: dbt-core-demo-schema  # 必須
      host: yourORG.databrickshost.com # 必須
      http_path: /SQL/Our/HTTP/PATH # 必須
      token: dapiXXXXXXXXXXXXXXXXXXXXXXX # 必須 (トークンベースの認証を使用する場合の個人アクセストークン (PAT))
      threads: 1  # オプション、デフォルト値は1
      connect_retries: 3 # オプション、デフォルト値は1

    stage:  #   追加ステージターゲット
      type: databricks
      host: stage.db.example.com
      user: John_Smith
      password: <stage_password>
      port: 5432
      dbname: my_stage_db
      schema: analytics
      threads: 1

    prod:  # 追加のprodターゲット
      type: databricks
      host: prod.db.example.com
      user: John_Doe
      password: <prod_password>
      port: 5432
      dbname: my_prod_db
      schema: sales
      threads: 1

  target: dev # デフォルトとして選択されたターゲット名
```

```bash
dbt run --target prod
```

注: データベース スキーマが存在しない場合は、dbt によってスキーマを作成するコードが追加されます。

#### ターゲット値の使用

`profiles.yml` ファイルには [`target` キーワード](https://docs.getdbt.com/reference/dbt-jinja-functions/target) が含まれており、その値はモデルのデプロイ先となる選択された/ターゲット環境です。

dbt はターゲットオブジェクトを作成し、以下のフィールドを設定します。

- target.profile_name
- target.name
- target.schema
- target.type *("postgres", "snowflake", "bigquery", "redshift", "databricks")*
- target.threads
- ...（データ プラットフォーム固有の値）

モデル内または `properties.yml` ファイル内（Jinja が使用できる場所であればどこでも）で、この `target` 値を条件付きで使用できます。

1. モデル内で target を使用する:

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

1. `*.yml` ファイル内のターゲットの使用:

    `models/sources.yml`

    ```yml
    version: 2
    sources:
        - name: sources
        database: |
            {%- if  target.name == "dev" -%} raw_dev
            {%- elif target.name == "stage"  -%} raw_stage
            {%- elif target.name == "prod"  -%} raw_prod
            {%- endif -%}
        schema: raw_data
        tables:
            - name: sales
            - name: marketing
        ...
    ```

    ターゲットに応じて、使用するデータベースを動的に選択できます。

### Config

dbtプロジェクトを三つの場所をで構成できます。

1. `config()` macro
1. `*.yml` files
1. `dbt_project.yml` file

### Modelの構成

テーブルやビューへのエイリアスの設定、マテリアライゼーションの指定など、[モデルを構成](https://docs.getdbt.com/docs/build/sql-models#configuring-models)できます。

モデルは3つの場所で構成できます（優先順位の高い順）。

1. `config()` macro
1. `*.yml` files
1. `dbt_project.yml` file

`config()` マクロはモデルファイルに埋め込まれているため、1つのモデルのみを設定できます。
`*.yml` ファイルでは複数のモデルを設定できますが、各モデルの名前を定義する必要があります。
`dbt_project.yml` ファイルでは複数のモデルを設定でき、フォルダパスも使用できます。

- `dbt_project.yml`

    ```yaml
    models:
      # モデル設定をプロジェクト名に名前空間化する必要があります
      my_dbt_project:
        sub_folder_A: # 以下の設定は、このサブフォルダ内のすべてのモデルに影響します
          +materialized: table
          +sql_header: <string>
          run_after: sql_statement
    ```

- `models/properties.yml`

    ```yml
    version: 2

    models:
      - name: model_1
        config:
          materialized: tab;e
          columns:
            - id
            - name

      - name: model_2
        config:
          materialized: tab;e
          columns:
            - id
            - name
    ```

- `models/my_simple_model.sql`

    ```sql
    {{ config(
        materialized="table",
        schema="sales",
        alias="transformed_orders",
        tags=["order", "inventory"]
    ) }}

    select
    ...
    from orders
    ```

#### 例

デフォルトでは、すべてのモデルは `VIEWS` として作成されます。
これは簡単に変更できます。

1. `dbt_project.yml` file.

    ```yaml
    name: my_dbt_project
    version: 1.0.0
    config-version: 2
    ...
    clean-targets:
      - "target"
      - "dbt_packages"
    ...
    models:
      my_dbt_project: # プロジェクト名は、この構成がこのプロジェクト内のモデルをターゲットにすることを意味します
        +materialized: table
        sales:
          # models/sales 内のすべてのモデルをビューとして具体化する
          +materialized: view
        events:
          # モデル/イベント内のすべてのモデルをビューとして具体化する
          +materialized: view
    ```

    `models/sales` および `models/events` サブフォルダ内のすべてのファイルは `Views` として作成され、`models` フォルダ内の残りのファイルは `Tables` として作成されます。

1. ymlファイル内

    `models/properties.yml`

    ```yaml
    version: 2
    models:
      - name: budgets # モデル名
        config:
          materialized: table
        columns:
          - id:
            data_tests:
              - unique
              - not_null
    ...
    ```

1. モデル内で直接

    ```sql
    {{ config(materialized='table') }}

    select
        id as user_id
        ...
    from customers
    ```

**エイリアスの設定:**

1. `dbt_project.yml`

    ```yaml
    models:
      my_dbt_project:
        orders:
          inventory: # dbtプロジェクト内のモデル名 (models/orders/inventory.sql)
            +alias: transformed_inventory_data # データベースに作成されるテーブル/ビューの名前
    ```

1. `models/properties.yml`

    ```yaml
    version: 2

    models:
      - name: inventory: # dbtプロジェクト内のモデル名
        config:
          alias: transformed_inventory_data # データベースに作成されるテーブル/ビューの名前
    ```

1. `confi()` macro

    `models/inventory.sql`

    ```sql
    {{ config(
    alias="sales_dashboard",
    materialized='table'

    ) }}

    select
    ...
    from raw_inventory
    ```

### 解析とコンパイル

Jinja で解析されたモデルは、`target/compiled/<project_name>/models/` フォルダにあります。
`dbt compile` コマンドはモデルを解析しますが、実行はしません（プラットフォームに送信しません）。

コンパイルされた（最終）モデルは、`target/run/<project_name>/models` フォルダにあります。
`dbt run` コマンドはモデルを解析し、実行します（プラットフォームに送信します）。

### コマンド

dbt core はコマンドラインツールです。`dbt --help` コマンドを実行すると、利用可能なコマンドの概要が表示されます。

**dbt run --select|--exclude:**

- `dbt run`: すべてのモデルをコンパイルして実行します。
- `dbt run --select "my_model.sql"`: 特定のモデルをコンパイルして実行します。
- `dbt run -s "my_model.sql"`: 特定のモデルをコンパイルして実行します。
- `dbt run --select "sub_folder"`: 特定のフォルダ内のすべてのモデルをコンパイルして実行します。
- `dbt run --exclude "my_model.sql"`: 特定のモデルを除くすべてのモデルをコンパイルして実行します。
- `dbt run --exclude "sub_folder"`: 特定のフォルダ内のモデルを除くすべてのモデルをコンパイルして実行します。

**dbt ls:**

特に `--exclude` オプションを使用する場合、どのモデルが実行されるかがわかりにくい場合があります。
実行されるノードのリストを確認するには、「dbt ls」コマンドを使用できます。

```bash
dbt ls --exclude "sub_folder"
```

## dbt Fusion エンジン

dbt チームは新しいソフトウェア、dbt Fusion エンジンを開発中です。Rust で記述されており、まだベータ版（開発版）です。
dbt Fusion エンジンは、dbt Core よりもはるかに高速になります。
dbt Core のすべての機能に加え、dbt モデル内の不正な SQL の検出、インライン CTE のプレビューなど、さらに多くの機能を備えています。

注: dbt Core は Python で記述されています。

Fusion には、ソースコード、独自仕様のコード、オープンソースコードが混在しています。

## ベストプラクティス

dbt labs チームは、以下のベストプラクティスを推奨しています。

1. Git などのバージョン管理ツールを使用します。モデルを削除すると、テーブル/ビューが何度も再作成されるのを防ぐことができるため、履歴を保存することは特に有効です。
1. プロファイル内のターゲットを使用して、本番環境と開発環境を分離します。
1. 環境変数を使用して、[`env_var` 関数](https://docs.getdbt.com/reference/dbt-jinja-functions/env_var) を使用し、機密性の高い認証情報を読み込みます。この関数は、`profiles.yml` ファイル、`dbt_project.yml` ファイル、および Jinja が使用できるあらゆる場所で使用できます。
1. `models` ディレクトリ内のモデルをディレクトリにグループ化します。

[推奨されるベストプラクティス](https://docs.getdbt.com/best-practices/best-practice-workflows#best-practice-workflows)

## リンク

- [What is dbt](https://docs.getdbt.com/docs/introduction#the-power-of-dbt)
- [dbt-utils](https://github.com/dbt-labs/dbt-utils): dbt プロジェクト用のユーティリティ関数。
