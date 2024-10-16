# SQLFluffの使う方

![cover photo](./images/cover.webp)

コードを書いた後に実行したとき、エラーが発生するとイライラします。さらに厄介なのは、そのエラーの原因が分からないときです。また、複数のメンバーがいる大規模なプロジェクトでは、メンバーごとにコードの書き方が異なる傾向があり、その結果、コードレビューが難しくなり、ソースコードに不整合が生じます。コードを実行する前にエラーを検出できた方が良いと思いませんか？さらに、チームメンバー全員が同じフォーマットでコードを書けば、もっと効率的になるでしょう。

SQLFluffと言うツールがこの全ての事を実現させます。

## SQLFluffは何でしょう？

SQLFluffは、SQLファイル用の最も人気のあるリンターです。構文エラーを検出すると、そのエラーが発生した行番号や位置、エラーの原因が表示されます。SQLFluffはエラーの検出だけでなく、SQLコードのフォーマットや構文エラーの修正も可能です。PostgreSQL、MySQL、Google BigQuery、Snowflakeなど、複数の[SQL 言語][dialects]をサポートしています。つまり、SQLコードを実行する前に構文エラーを検出・修正できるので、非常に役立ち、重要な作業に集中することができます。また、SQLFluffは非常に設定が簡単で、コンマの位置、文字の大文字小文字、インデントなどのルールを簡単に設定できます。

エンジニアは自分のパソコンにSQLFluffをインストールし、SQLFluffを利用してコードのエラーを検出・修正した後にGitにコミットし、GitLabやGitHubなどにプッシュすることをお勧めします。
_全てのドキュメントはこちらにあります_: [Docs][SQLFluff Docs]。

## インストール

SQLFluff は以下のようにインストールできます

- VSCode エクステンション
- プリコミットフック
- コマンドラインツール
- CI/CDパイプラインツール

SQLFluffをコマンドラインツールとして設定し、実行してくださいのが一番簡単です。また、この記事でプレコミットフックとしての使い方も説明します。

### SQLFluffをコマンドラインツールとしてインストール

**注意点：** SQLFluffをインストールするにはPythonとpip (またはpoetryやpipenvなどのパッケージマネージャ)が必要です。このマニュアルではpipを使用します。

ターミナルで以下のコマンドを実行して SQLFluff をインストールする：

```bash
pip install sqlfluff
```

インストールを確認する為に、以下のコマンドを実行してください:

```bash
sqlfluff version
# 3.2.4
```

## 使う方

SQLFluffには3つの主要なコマンドがあります：
`lint` : 構文エラーを表示します。
`format` : コードを整形する（主に改行、インデテーション、空白を修正する）。
`fix`: カンマ、セミコロン、順番、改行などの構文エラーを修正します。

test.sqlというファイルを`lint`する為に、以下のコマンドを実行してください：

```bash
sqlfluff lint test.sql --dialect snowflake
```

上のコマンドの結果:

```bash
== [test.sql] FAIL
L:   1 | P:   1 | LT01 | Expected only single space before 'SELECT' keyword.
                       | Found '  '. [layout.spacing]
L:   1 | P:   1 | LT02 | First line should not be indented.
                       | [layout.indent]
L:   1 | P:   1 | LT13 | Files must not begin with newlines or whitespace.
                       | [layout.start_of_file]
L:   1 | P:  11 | LT01 | Expected only single space before binary operator '+'.
                       | Found '  '. [layout.spacing]
L:   1 | P:  14 | LT01 | Expected only single space before naked identifier.
                       | Found '  '. [layout.spacing]
L:   1 | P:  27 | LT01 | Unnecessary trailing whitespace at end of file.
                       | [layout.spacing]
L:   1 | P:  27 | LT12 | Files must end with a single trailing newline.
                       | [layout.end_of_file]
All Finished 📜 🎉!
```

**リント出力の説明:**

リント出力には、エラーの原因となった`L`（行番号）と `P`（位置）、そしてエラーを見つけたルール・インデックス（この場合はLT01）が表示される。ルール・インデックスの後には、何が問題なのかについての短い説明がある。
_すべてのルールとその定義は、こちらをご覧ください:[Rule Index]_

SQLFluff にはデフォルトのルールが用意されています。これらのルールはコマンドラインでもすぐに確認出来ます：

```bash
sqlfluff rules
```

チェックするルールを指定したり、特定のルールを除外したりすることが出来ます。
ルールを指定する方法:

```bash
sqlfluff lint test.sql --rules LT02,LT12,CP01,ST06,LT09,LT01
```

ルールを除外する方法:

```bash
sqlfluff fix test.sql --exclude-rules LT01
```

SQLFluffはあるSQL言語が使用するいくつかのキーワードを理解出来ない場合があります。
このような場合、`parsing error`が発生します。この問題を回避する為に、SQLFluffに`parsing error`を無視するように指示する事が出来ます。

```bash
sqlfluff fix test.sql --ignore parsing
```

全てのコマンドライン設定はこちらをご覧ください: [CLI Config]。

## 設定ファイル

SQLFluffがデフォルトの設定があり、デフォルトの設定を上書きすることも可能です。SQLFluffを`cli`で設定したくない場合は、設定ファイルを書く事が出来ます。
SQLFluffデフォルトの設定をファイルとしてこちらでご確認出来ま: [Config File]。

SQLFluff は以下の設定ファイルをサポートします：

- setup.cfg
- tox.ini
- pep8.ini
- .sqlfluff
- pyproject.toml

以下の例では、7つのコンフィギュレーション ルールを変更します。残りのルールはデフォルトのままです。

`.sqlfluff` ファイルとして

```bash
[sqlfluff]

dialect = snowflake

exclude_rules = ST06

runaway_limit = 2

large_file_skip_byte_limit = 2000000

[sqlfluff:layout:type:comma]
line_position = leading
```

同じ設定は、TOMLファイルでは次のようになります:

```TOML
[tool.sqlfluff]

dialect = snowflake

exclude_rules = ST06

runaway_limit = 2

large_file_skip_byte_limit = 2000000

[tool.sqlfluff.layout.type.comma]
line_position = leading
```

**記の設定の説明:**

`dialect = snowflake` SQLFluff の方言を Snowflake 構文に設定します。`exclude_rules = ST06` はルール `ST06`を除外する設定です。`ST06`ルールはselect対象を複雑さの昇順に並べます。例えば、`ST06`ルールが`*`を他のselect項目の上に置きます：

```SQL
select
    *,
    a,
    b,
    row_number() over (partition by id order by date) as y
from my_table
```

でも、僕は列の順番を変わったくないので、`ST06`ルールを除外する設定を書いています。

`runaway_limit = 2` 次コードブロックに進む前に、SQLFluff が、コードブロックからエラー探し、改善を試み回数の制限。`large_file_skip_byte_limit = 2000000`, SQLファイルが2000000バイト(2MB)を超える場合、SQLFluffはそのファイルを無視します。`line_position = leading` は各行の先頭にカンマを置きます。
`line_position = leading`ルールの結果:

```SQL
Select
    a
    ,b
    ,c
From my_table;
```

## プレコミット

Git はすべての開発者にとって欠かせないツールです。バージョン管理とコラボレーションに役立ちます。Gitが通常の作業を行う際にいくつかの関数を呼び出すことができます。たとえば、変更をリポジトリにコミットする前に、git は特定の関数を呼び出すことができます。これらの関数は、プレコミットフックと呼ばれます。これらの関数（pre-commit hooks）の設定や構成を支援する[pre-commit]と言うツールがあります。

### プレコミットの設定

```bash
$ pip install pre-commit

# check installation
$ pre-commit --version
# pre-commit v4.0.1
```

レポジトリのルートフォルダーに`.pre-commit-config.yaml`というファイルを作成します。
中に以下のコードを書きます:

```yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.1.4
    hooks:
      - id: sqlfluff-lint
      - id: sqlfluff-fix
```

`pre-commit`は`.sqlfluff`の設定を使うことができます。しかし、`.sqlfluff`ファイルを使用したくない場合は、以下のように`.pre-commit-config.yaml`ファイルに直接設定を記述することができます。

```yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.1.4
    hooks:
      - id: sqlfluff-lint
        args:
            - '--dialect'
            - 'snowflake'
            - '--exclude-rules'
            - 'ST06'
            - '--runaway-limit'
            - '2'
            - '--layout-type'
            - 'comma'
            - '--line-position'
            - 'leading'

      - id: sqlfluff-fix
            args:
            - '--dialect'
            - 'snowflake'
            - '--exclude-rules'
            - 'ST06'
            - '--runaway-limit'
            - '2'
            - '--layout-type'
            - 'comma'
            - '--line-position'
            - 'leading'
```

SQLFluffのpre-commit関数をセットアップする為に、`pre-commit install` を実行してください。これで、`git commit` を実行するたびに、コミット前に SQLFluff の linting コマンドと修正コマンドが実行されます。SQLFluff がエラーを見つけなければコミットされますが、エラーが見つかった場合はコミットされません。SQlFluff はエラーをターミナルに出力し、可能な限り修正します。その後、`git add` コマンドと `git commit` コマンドをもう一度実行する必要があります。

[SQLFluff docs]: https://docs.sqlfluff.com/en/stable/
[Rule Index]: https://docs.sqlfluff.com/en/stable/rules.html#rule-index
[Dialects]: https://docs.sqlfluff.com/en/stable/dialects.html
[CLI Config]: https://docs.sqlfluff.com/en/stable/cli.html#cliref
[Config File]: https://docs.sqlfluff.com/en/stable/configuration.html#default-configuration
[pre-commit]: https://pre-commit.com/
