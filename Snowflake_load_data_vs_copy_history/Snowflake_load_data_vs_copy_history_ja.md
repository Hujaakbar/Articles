# Snowflakeで Load History vs Copy History

![data](./images/data.jpg)

Snowflake で Load History を使っても Copy History を使ってもテーブルにロードされた過去のデータの履歴を取得できるようになります。

じゃあ、何が違いますか。いつどっちを使った方が良いでしょうか。

## Load History と Copy History の７違いさ

### 違いさ１: ビュー vs テーブル関数

Load History は[ビュー](https://docs.snowflake.com/ja/sql-reference/info-schema/load_history)です。
Copy History と言う[テーブル関数](https://docs.snowflake.com/ja/sql-reference/functions/copy_history)も[ビュー](https://docs.snowflake.com/ja/sql-reference/account-usage/copy_history)もあります。

Load History の使う方の例：

```sql
USE DATABASE db_1;

SELECT table_name, last_load_time
  FROM information_schema.load_history
  WHERE schema_name=current_schema() AND
  table_name='TABLE_1';
```

Copy History ビュー:

```sql
select file_name, table_name, last_load_time
from snowflake.account_usage.copy_history
order by last_load_time desc
limit 10;
```

Copy History テーブル関数:

```sql
select *
from table(
    information_schema.copy_history(
        TABLE_NAME=>'TABLE_1', START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())
        )
    )
;
```

### 違いさ２: アクセス権限

Copy History テーブル関数は普通の関数です。
Copy History ビューは Account Usage ビューを使用します。
Load History ビュー Information Schema ビューを使用します。

と言うは：
Load History ビューを使うに Copy History テーブル関数使うよりもっと権限が必要です。
Copy History ビューを使うには Load History ビューを使うよりもっと高く権限が必要です。

### 違いさ 3: Snowpipe を使用してロードされたデータの履歴

Load History ビューは、Snowpipe を使用してロードされたデータの履歴を返しません。
Copy History テーブル関数もビューも Snowpipe を使用してロードされたデータの履歴を返します。

### 違いさ 4: 返される行の上限

Load History ビューは, 10,000 行の上限を返します。
Copy History テーブル関数もビューもこの上限がないです。

### 違いさ 5: 過去履歴の上限

Load History ビューと Copy History テーブル関数はテーブルにロードされた過去 14 日間以内のデータの履歴を取得できるようになります。
Copy History ビューは過去 365 日（1 年）の Snowflake データロード履歴をクエリできます。

### 違いさ 6: レイテンシー

Copy History ビューは多くの場合、ビューの遅延は最大 120 分（2 時間）です。状態によって最大 2 日になることもあります。

### 違いさ 7: クエリーの結果

Copy history テーブル関数を使う時に、必ずテーブル名を指定しないといけないです。
と言うのは、Copy history テーブル関数は一つのテーブルだけにロードされた過去のデータの履歴を取得できます。

例：

```sql
select *
from table(
    information_schema.copy_history(
        TABLE_NAME=>'TABLE_1', START_TIME=> DATEADD(hours, -1, CURRENT_TIMESTAMP())
        )
    )
;
```

Load History ビューと Copy history ビューの場合ではテーブル名を指定するのはオプショナルでは。
例： database_a データベースに対して実行された 10 個の最新の COPY INTO コマンドのレコードを取得します。

```sql
USE DATABASE database_a;

SELECT table_name, last_load_time
  FROM information_schema.load_history
  ORDER BY last_load_time DESC
  LIMIT 10;
```
