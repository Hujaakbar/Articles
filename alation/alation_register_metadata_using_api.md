# Alation: APIを使用してメタデータを登録する

## Alation

データセット、レポート、その他アセットが、AWS、Azure、GitHub、Power BIなどの環境に散在している場合、必要な情報（どのデータがどこにあるのか）を探し出すのに何日もかかることがあります。**メタデータ管理**は、現代のデータ戦略の要です。熟練した司書のように、適切なデータが目録化され、簡単に見つけられ、適切に維持され、組織のニーズに合っていることを保証します。そのためのメタデータ管理ソリューションの一つが **Alation** です：[Alationの概要](https://youtu.be/JehUtA6PVv4?feature=shared)。

## コネクタ

Alationは120以上のソースに対応したコネクタを提供しています： [全コネクタ一覧](https://www.alation.com/product/connectors/all-connectors/)。

Alationはメタデータの大部分を自動的に抽出できますが、すべてではありません。 DenodoとAlationの例を見てみましょう。AlationにはDenodo用のコネクタがあります。

- [Denodoコネクタ](https://www.alation.com/docs/en/latest/OpenConnectorFramework/DataSourceConnectors/Denodo/DenodoOCFConnectorOverview.html)
- [Denodoによる連携説明](https://community.denodo.com/kb/en/view/document/How%20to%20integrate%20Alation%20with%20Denodo)

対応している認証方法：

- ユーザー名とパスワードによる認証
- SSL認証

Alationは以下のメタデータを自動的に抽出します。

- スキーマのリスト
- テーブルのリスト
- ビューのリスト
- カラムのリスト
- データの利用頻度
- 抽出されたテーブルの主キー情報
- 抽出されたテーブルからのデータサンプル取得
- 抽出されたカラムからのデータサンプル取得

**ただし、以下のメタデータはコネクタで抽出できません。**

- カラムのコメント
- カラムのデータ型
- ソースのコメント

コネクタで抽出できないメタデータを補完するために、APIを使用することができます。

## カスタムフィールドの作成

APIを使ってデータソースにメタデータフィールドを追加する方法を説明する前に、まず**カスタムフィールド**について説明します。

AlationのUIでは、テーブルやスキーマなどのデータソースが「タイトル」や「説明」といったメタデータフィールドとともに表示されます。通常、これらのデフォルトのメタデータフィールドで十分ですが、新しい**カスタムフィールド**を追加する必要がある場合は、[追加することも可能](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/index.html)です。

Alationには、「タイトル」や「説明」といった[組み込みフィールド](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/AboutTemplatesAndFields.html)があります。これに加えて、カスタムフィールドを作成することも可能です。カスタムフィールドは再利用可能なオブジェクトです。
カスタムフィールドは**オブジェクトテンプレート**に紐づけられます。オブジェクトテンプレートは、テーブル、スキーマ、カラムといったオブジェクトの種類ごとに、メタデータの表示方法を定義します。
ほぼ全ての同じ種類のオブジェクトは共通のテンプレートを共有しています。つまり、一つのテンプレートが同じ種類のすべてのオブジェクトに適用されます。例えば、すべてのスキーマは同じスキーマテンプレートを使用します。

カスタムフィールドを（スキーマに）追加する手順：

1. カタログ管理者またはサーバー管理者の役割が必要です。
2. [カスタムフィールドを作成](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/ManageCustomFields.html?version=neo)します。
3. 新しく作成したカスタムフィールドを追加して（スキーマ）[テンプレートを編集](https://www.alation.com/docs/en/latest/steward/TemplatesAndCustomFields/ManageTemplates.html#edit-a-template)します。

![graph](https://imgur.com/pLOVpGL.png)
*（AI生成画像のため、テキストに一部不正確な箇所があります）*

注意：AlationはすべてのカスタムフィールドにIDを割り当てます。例えば、カスタムフィールドのタイトルが "Data Sensitivity" で、その `field_id` が 1002 のようになります。

## API

### Upload Logical Metadata (ULM) API

古いAPI、Upload Logical Metadata (ULM) APIがあります。このAPIは非推奨です。**使用しないでください**（AlationはULM APIの使用を推奨していません）。

[Upload Logical Metadata (ULM) API 非推奨化](https://docs.alation.com/en/latest/releases/releasenotes/ReleaseNotes20243.html#upload-logical-metadata-ulm-api-deprecation)

### Relational Integration API

タイトル、説明、カスタムフィールドを更新するには、[Relational Integration API](https://developer.alation.com/dev/reference/relational-integration-api-v2-overview)を使用します。

必要な権限：データソースビューアまたはデータソース管理者

API呼び出しあたりのペイロード制限：

|オブジェクトタイプ|POSTペイロードの最大オブジェクト数|
|----|----|
|スキーマ|1,000|
|テーブル|1,000|
|カラム|10,000|

[スキーマの更新例](https://developer.alation.com/dev/reference/patchschemas)

```python
import requests

url = "https://alation_domain/integration/v2/schema/"

payload = [
    {
        "key": "95.employees", # スキーマ名は employees
        "title": "Schema for employees data.",
        "description": "Stores all the tables related to employees from marketing department.",
        "db_comment": "This schema is part of company database storing important PII data.",
        "custom_fields": [
             {
            "field_id": 101,
            "value": "Finance Team"       // Business Owner カスタムフィールド
            "op": "replace"
            },
            {
            "field_id": 102,
            "value": "Highly Confidential" // Data Sensitivity カスタムフィールド
            "op": "replace"
            }
        ]
    }
]
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "TOKEN": "my_secret_token"
}

response = requests.patch(url, json=payload, headers=headers)

print(response.text)
```

|用語|説明|
|---|---|
|key|スキーマやテーブルなどの名前|
|title|スキーマやテーブルのタイトル（データベースには存在せず、Alationのカタログ内にのみ存在します）|
|db\_comment|データソースから取得したスキーマのコメント|
|op|カスタムフィールドで実行する操作です。`add`、`remove`、`replace`のいずれかです。`add`と`remove`はMULTI\_PICKERとOBJECT\_SETにのみ適用可能です。`replace`はすべてのカスタムフィールドに適用可能です。|

`custom_fields`はオブジェクトの配列である必要があります。
AlationはすべてのカスタムフィールドにIDを割り当てます。例えば、カスタムフィールドのタイトルが "Data Sensitivity" で、その `field_id` が 1002 のようになります。
しかし、**Relational Integration APIでは新しいカスタムフィールドを作成することはできません**。更新のみ可能です。

> これらのカスタムフィールドは、まずスキーマのotypeテンプレートに関連付ける必要があります。UIの「Customize Catalog」オプションから、新しいカスタムフィールドを作成し、スキーマのotypeテンプレートに追加することができます。

### Custom Field Value API

[Custom Field Values Async API](https://developer.alation.com/dev/reference/putcustomfieldvaluesasync)を使用してカスタムフィールドを更新できます。

注意：Custom Field Value APIでは、スキーマ、テーブル、カラムのタイトルや説明は更新できません。代わりにRelational Integration APIを使用してください。

制限：1リクエストあたり最大10,000オブジェクト

```python
import requests

url = "https://alation_domain/integration/v2/custom_field_value/async/"

payload = [
    {
        "field_id": 10006, # カスタムフィールドID
        "oid": 5,  # このカスタムフィールドが属するオブジェクトのID
        "otype": "table", # このフィールドが属するオブジェクトのタイプ
        "ts_updated": "2025-09-10T07:07:33.884Z",
        "value": "my custom field value"
    },
    {
        "field_id": 10007,
        "oid": "7", # このカスタムフィールドが属するオブジェクトのID
        "otype": "attribute", # このフィールドが属するオブジェクトのタイプ
        "ts_updated": "2025-09-10T07:07:33.884Z",
        "value": ["high, medium, low"]
    }
]
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "TOKEN": "my_secret_token"
}

response = requests.put(url, json=payload, headers=headers)

print(response.text)
```
