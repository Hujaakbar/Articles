# Snowflake Data Cloud Summit 2024 Summary

![snow_summit](./images/snow_summit.jpg)

2024 念６月の３~６日 San Francisco で[Snowflake Data Cloud Summit 2024](https://www.snowflake.com/summit/)が行おいました。主なトピックは AI と Polaris Catalog で、スターゲストが NVidia の CEO [Jensen Huang](https://en.wikipedia.org/wiki/Jensen_Huang)でした。
この記事がその Data Cloud Summit をサマライズします。

## AI

### Snowflake Arctic

-   Arctic AI は Snowflake が自分で開発した AI モデルです
-   Open Source です
-   Snowflake によると Meta の Llama3 8B AI モデルよりもっと良いです

[リンク](https://www.snowflake.com/en/blog/arctic-open-efficient-foundation-language-models-snowflake/)

### Universal Search

[Universal Search](https://docs.snowflake.com/ja/user-guide/ui-snowsight-universal-search)を使用すると、アカウント内のデータベース オブジェクト、Snowflake Marketplace で利用可能なデータ製品、関連する Snowflake ドキュメントのトピック、関連する Snowflake コミュニティ ナレッジ ベースの記事をすばやく簡単に見つけることが出来ます。

Universal Search は、クエリとデータベース オブジェクトに関する情報を理解し、検索語とは異なる名前のオブジェクトを見つけることができる。スペルを間違えたり、検索語の一部だけを入力したりした場合でも、役立つ結果が表示されます。

テーブルの列名によっても、Universal Search は結果を検索出来ます。列名、テーブルの行に書いたおりデータじゃないです。

### Document AI

PDF, 絵、ビデオ、audio ファイルからデータを抽出出来る AI を Snowflake で使うようになりました。
[リンク](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/overview)

### Snowflake Copilot

-   SQl コードを書くに助ける[AI アシスタント](https://www.snowflake.com/blog/copilot-ai-powered-sql-assistant/)です
-   普通の言葉を SQL コードに変わります: text-to-SQL

### ML Functions

-   Snowflake でデータを予測する、異常検出、Classification (グルーップング)等を出来るＭＬ関数(モデル)が発表しました
-   この ML 関数を直接に使えない、この ML 関数を使って、自分の AI モデルを開発し、そして、開発した AI モデルを使えます。
    [リンク](https://docs.snowflake.com/en/guides-overview-ml-functions)

### NVIDIA AI

-   AI を開発する為に使う NVIDIA NeMo Retriever と NVIDIA Triton Inference Server を Snowflake で使うようになりました
-   NeMo Retriever はチャットボット アプリケーションのパフォーマンスとスケーラビリティを向上します

## Polaris Catalog

Snowflake で Apache Iceberg を使えるようになりました

-   [Polaris Catalog](https://other-docs.snowflake.com/en/polaris/overview)は Apache Iceberg を利用出来るサービスです
-   Polaris Catalog は Open Source です
    データは Apache Iceberg に保存され、Polaris Catalog で Apache Iceberg に保存されているデータをクエリー、データを入力する等の事をします。
-   Apache Iceberg は **Open Source**ので、Apache Iceberg に保存されているデータを Snowflake じゃなくて、他のサービスでも使えます
-   Apache Iceberg はテーブルのフォーマット(データが保存される方法とフォーマット)。
    テーブル・フォーマットの機能は、テーブルを構成するすべてのファイルをどのように管理、整理、追跡するかを決定することであります。
-   元に Apache Hive に代わりに、Netflix が Iceberg を開発し、今は Apache Foundation が運用しています。
-   メリットは早くて、 効率的で信頼できます
-   凄く大きなテーブルをサポート出来ます
-   SQL 言語を使えます
-   テーブルを（列を消す、列を追加する等）修正出来ます
-   **データのバージョン管理**: Apache Iceberg はデータのバージョン管理をサポートしており、ユーザーは時間経過に伴うデータの変更を追跡できる。これによりタイムトラベル機能が有効になり、ユーザーはデータの履歴バージョンにアクセスしてクエリを実行し、更新と削除の間のデータの変更を分析できます。
-   似ているフォーマットの[Delta Lake よりも Apachi Hudi よりも早いです][Apache Iceberg3]
-   今月(末)に Snowflake で Preview 出来ます
-   [Microsoft Fabric](https://venturebeat.com/data-infrastructure/microsoft-adds-iceberg-support-to-fabric-partners-with-snowflake-for-bi-directional-data-access/)も同じデータをアクセス出来、データをコピーする必要がないです

[Apache Iceberg3]: https://www.ibm.com/topics/apache-iceberg

---

## その他のアップデート

### Snowflake Notebooks

-   Snowflake が Notebooks をサポートするようになりました
-   同じページに SQL、Python と Markdown を書けます
-   Notebook で Streamlit も使えます

### Snowflake Data Clean Rooms

-   データを権限管理を利用しながら、安全的に共有出来ます
-   Snowflake Data Clean Rooms に中で PII を消されり、データが匿名化されたデータになます
-   (Raw)詳細なデータを見なず、他の会社/相手のデータを分析出来る: Join, Group By, Count, Min, Max 等のクエリー

### Coda で Snowflake のデータを使えるようになりました

Coda は Notion ようなウェブアプリケーションで、Coda でドクメントを作成することが出来、他の Gmail, Slack ようなアプリを導入し、Coda から使える事が出来ます。

### CREATE OR ALTER TABLE and CREATE OR ALTER TASK

`CREATE OR REPLACE`ような、`CREATE OR ALTER`コマンドがサポートされています (プレビュー)
もし、テーブルがあったら修正される、なかったら作成されます
