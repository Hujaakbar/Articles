# Snowflake Data Cloud Summit 2024 Summary

2024念６月の３~６日San Franciscoで[Snowflake Data Cloud Summit 2024](https://www.snowflake.com/summit/)が行おいました。主なトピックはAIとPolaris Catalogで、スターゲストがNVidiaのCEO[Jensen Huang](https://en.wikipedia.org/wiki/Jensen_Huang)でした。
この記事がそのData Cloud Summitをサマライズします。

## AI

### Snowflake Arctic

- Arctic AIはSnowflakeが自分で開発したAIモデルです
- Open Sourceです
- SnowflakeによるとMetaのLlama3 8B AIモデルよりもっと良いです

[リンク](https://www.snowflake.com/en/blog/arctic-open-efficient-foundation-language-models-snowflake/)

### Universal Search

[Universal Search](https://docs.snowflake.com/ja/user-guide/ui-snowsight-universal-search)を使用すると、アカウント内のデータベース オブジェクト、Snowflake Marketplace で利用可能なデータ製品、関連する Snowflake ドキュメントのトピック、関連する Snowflake コミュニティ ナレッジ ベースの記事をすばやく簡単に見つけることが出来ます。

Universal Searchは、クエリとデータベース オブジェクトに関する情報を理解し、検索語とは異なる名前のオブジェクトを見つけることができる。スペルを間違えたり、検索語の一部だけを入力したりした場合でも、役立つ結果が表示されます。

テーブルの列名によっても、Universal Searchは結果を検索出来ます。列名、テーブルの行に書いたおりデータじゃないです。

### Document AI

PDF, 絵、ビデオ、audioファイルからデータを抽出出来るAIをSnowflakeで使うようになりました。
[リンク](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai/overview)

### Snowflake Copilot

- SQlコードを書くに助ける[AI アシスタント](https://www.snowflake.com/blog/copilot-ai-powered-sql-assistant/)です
- 普通の言葉をSQLコードに変わります:  text-to-SQL

### ML Functions

- Snowflakeでデータを予測する、異常検出、Classification (グルーップング)等を出来るＭＬ関数(モデル)が発表しました
- このML 関数を直接に使えない、このML 関数を使って、自分のAIモデルを開発し、そして、開発したAIモデルを使えます。
[リンク](https://docs.snowflake.com/en/guides-overview-ml-functions)

### NVIDIA AI

- AIを開発する為に使うNVIDIA NeMo RetrieverとNVIDIA Triton Inference ServerをSnowflakeで使うようになりました
- NeMo Retriever はチャットボット アプリケーションのパフォーマンスとスケーラビリティを向上します

## Polaris Catalog

SnowflakeでApache Icebergを使えるようになりました

- [Polaris Catalog](https://other-docs.snowflake.com/en/polaris/overview)はApache Icebergを利用出来るサービスです
- Polaris CatalogはOpen Sourceです
データはApache Icebergに保存され、Polaris CatalogでApache Icebergに保存されているデータをクエリー、データを入力する等の事をします。
- Apache Icebergは **Open Source**ので、Apache Icebergに保存されているデータをSnowflakeじゃなくて、他のサービスでも使えます
- Apache Icebergはテーブルのフォーマット(データが保存される方法とフォーマット)。
テーブル・フォーマットの機能は、テーブルを構成するすべてのファイルをどのように管理、整理、追跡するかを決定することであります。
- 元にApache Hiveに代わりに、NetflixがIcebergを開発し、今はApache Foundationが運用しています。
- メリットは早くて、 効率的で信頼できます
- 凄く大きなテーブルをサポート出来ます
- SQL言語を使えます
- テーブルを（列を消す、列を追加する等）修正出来ます
- **データのバージョン管理**: Apache Iceberg はデータのバージョン管理をサポートしており、ユーザーは時間経過に伴うデータの変更を追跡できる。これによりタイムトラベル機能が有効になり、ユーザーはデータの履歴バージョンにアクセスしてクエリを実行し、更新と削除の間のデータの変更を分析できます。
- 似ているフォーマットの[Delta LakeよりもApachi Hudiよりも早いです][Apache Iceberg3]
- 今月(末)にSnowflakeでPreview出来ます
- [Microsoft Fabric](https://venturebeat.com/data-infrastructure/microsoft-adds-iceberg-support-to-fabric-partners-with-snowflake-for-bi-directional-data-access/)も同じデータをアクセス出来、データをコピーする必要がないです

[Apache Iceberg3]:https://www.ibm.com/topics/apache-iceberg

---

## その他のアップデート

### Snowflake Notebooks

- SnowflakeがNotebooksをサポートするようになりました
- 同じページにSQL、PythonとMarkdownを書けます
- NotebookでStreamlitも使えます

### Snowflake Data Clean Rooms

- データを権限管理を利用しながら、安全的に共有出来ます
- Snowflake Data Clean Roomsに中でPIIを消されり、データが匿名化されたデータになます
- (Raw)詳細なデータを見なず、他の会社/相手のデータを分析出来る: Join, Group By, Count, Min, Max等のクエリー

### CodaでSnowflakeのデータを使えるようになりました

CodaはNotionようなウェブアプリケーションで、Codaでドクメントを作成することが出来、他のGmail, Slackようなアプリを導入し、Codaから使える事が出来ます。

### CREATE OR ALTER TABLE and CREATE OR ALTER TASK

`CREATE OR REPLACE`ように今は`CREATE OR ALTER`がある (プレビュー)
もし、テーブルがあったら修正される、なかったら作成されます
