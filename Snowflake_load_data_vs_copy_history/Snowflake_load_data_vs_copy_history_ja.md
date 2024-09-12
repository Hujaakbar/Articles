# Load History vs Copy History

SnowflakeでLoad Historyを使ってもCopy Historyを使ってもテーブルにロードされた過去のデータの履歴を取得できるようになります。

じゃあ、何が違いますか。いつどっちを使った方が良いでしょうか。

## Load History と Copy Historyの７違いさ

### 違いさ１: ビュー vs テーブル関数

Load Historyは[ビュー](https://docs.snowflake.com/ja/sql-reference/info-schema/load_history)です。
Copy Historyと言う[テーブル関数](https://docs.snowflake.com/ja/sql-reference/functions/copy_history)も[ビュー](https://docs.snowflake.com/ja/sql-reference/account-usage/copy_history)もあります。

Load Historyの使う方の例：

```sql
USE DATABASE db_1;

SELECT table_name, last_load_time
  FROM information_schema.load_history
  WHERE schema_name=current_schema() AND
  table_name='TABLE_1';
```

Copy Historyビュー:

```sql
select file_name, table_name, last_load_time 
from snowflake.account_usage.copy_history
order by last_load_time desc
limit 10;
```

Copy Historyテーブル関数:

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

Copy Historyテーブル関数は普通の関数です。
Copy HistoryビューはAccount Usageビューを使用します。
Load HistoryビューInformation Schemaビューを使用します。

と言うは：
Load Historyビューを使うにCopy Historyテーブル関数使うよりもっと権限が必要です。
Copy Historyビューを使うにはLoad Historyビューを使うよりもっと高く権限が必要です。

### 違いさ3: Snowpipeを使用してロードされたデータの履歴

Load Historyビューは、Snowpipeを使用してロードされたデータの履歴を返しません。
Copy Historyテーブル関数もビューもSnowpipeを使用してロードされたデータの履歴を返します。

### 違いさ4: 返される行の上限

Load Historyビューは, 10,000行の上限を返します。
Copy Historyテーブル関数もビューもこの上限がないです。

### 違いさ5: 過去履歴の上限

Load HistoryビューとCopy Historyテーブル関数はテーブルにロードされた過去14日間以内のデータの履歴を取得できるようになります。
Copy Historyビューは過去365日（1年）のSnowflakeデータロード履歴をクエリできます。

### 違いさ6: レイテンシー

Copy Historyビューは多くの場合、ビューの遅延は最大120分（2時間）です。状態によって最大2日になることもあります。

### 違いさ7: クエリーの結果

Copy historyテーブル関数を使う時に、必ずテーブル名を指定しないといけないです。
と言うのは、Copy historyテーブル関数は一つのテーブルだけにロードされた過去のデータの履歴を取得できます。

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

Load HistoryビューとCopy historyビューの場合ではテーブル名を指定するのはオプショナルでは。
例： database_a データベースに対して実行された10個の最新の COPY INTO コマンドのレコードを取得します。

```sql
USE DATABASE database_a;

SELECT table_name, last_load_time
  FROM information_schema.load_history
  ORDER BY last_load_time DESC
  LIMIT 10;
```
