# Snowflake ストアドプロシージャ

![sales](./images/sales.jpg)\
*Image by [Gerd Altmann](https://pixabay.com/users/geralt-9301/) from [Pixabay](https://pixabay.com//)*

この記事で Snowflake のストアドプロシージャは何かと使う方法を学びます。

## ストアドプロシージャと言うのは

ストアドプロシージャを関数の一つ種類と考えてもいいです。ストアドプロシージャを記述して、 SQL を実行する手続き型コードでシステムを拡張できます。ストアドプロシージャを作成すると、何度でも再利用できます。
値を明示的に返すことが許可されていますが、必須ではないです。プロシージャを実行するロールの権限ではなく、プロシージャを所有するロールの権限でコードを実行します。

サポートされている言語:

- Java
- JavaScript
- Python
- Scala
- Snowflake Scripting (SQL)

ストアドプロシージャの形：

```SQL
CREATE OR REPLACE PROCEDURE プロシージャ名(arguments argumentsのタイプ)
RETURNS レターんタイプ
LANGUAGE 言語 -- (例:python, JavaScript等)
-- RUNTIME_VERSION = '3.8' (言語がpython, java, scalaなら必要 )
-- PACKAGES = ('snowflake-snowpark-python') (言語がpython, java, scalaなら必要 )
-- HANDLER = 'run' (言語がpython, java, scalaなら必要 )
EXECUTE AS -- (CALLERか OWNER)
AS
$$
ロジック
$$;

```

SQL で書いたストアドプロシージャの例：

```SQL
CREATE OR REPLACE PROCEDURE concatenate_strings(
    first_arg VARCHAR,
    second_arg VARCHAR,
    third_arg VARCHAR DEFAULT ' default_argument '
)
  RETURNS VARCHAR
  LANGUAGE SQL
  AS
  $$
  BEGIN
    RETURN first_arg || second_arg || third_arg;
  END;
  $$;
```

プロシージャのロジックは**ハンドラー**と言わります。

ストアドプロシージャを呼び方：

```SQL
CALL procedure名(argument);
```

Snowflake が関数もストアドプロシージャもサポートしています。
一つの違いさは関数を`Select`と一緒に使いますが、ストアドプロシージャを`select`と一緒に使えないです。
だから、ストアドプロシージャを以下のような`DDL`または`DML`データベース操作の実行が必要に時に、使った方がいいです。

- 仮テーブルの削除、 N 日より古いデータの削除、ユーザーの追加など、DDL を含む管理タスク。
- DML ステートメント（例: `UPDATE` ステートメント）

ストアドプロシージャを三つの方法で呼べます。
上の例で作成した`concatenate_string`ストアドプロシージャを呼んでみましょう。

```SQL
CALL concatenate_strings('one_v0', 'two_v0', 'three_v0');

CALL concatenate_strings(first_arg => 'one_v1', second_arg => 'two_v1', third_arg => 'three_v1');

-- 順番が変わったいます。
CALL concatenate_strings(third_arg => 'three_v2', first_arg => 'one_v2', second_arg => 'two_v2');

-- 三番目のparameterがデフォルトの価値あるので、二つだけのArgumentを使うのはOkです。
CALL concatenate_strings('one_v3', 'two_v3');
```

## Security

ハンドラーコードは、制限されたエンジン内で実行されます。ハンドラーコードが大量のメモリを消費すると、エラーが返されます。ハンドラーの完了に時間がかかりすぎると、Snowflake は SQL ステートメントを強制終了し、ユーザーにエラーを返します。これにより、無限ループなどのエラーの影響およびコストが制限されます。
ハンドラーは外部ライブラリの機能を使用できますが、Snowflake のセキュリティ制限により、ファイルへの書き込みなど、一部の機能が無効になります。
ストアドプロシージャはアトミックではありません。ストアドプロシージャ内の 1 つのステートメントが失敗した場合、ストアドプロシージャ内の他のステートメントは必ずしもロールバックされるとは限りません。

ストアドプロシージャは、 SQL ステートメントを動的に作成して実行できます。ただし、これにより、特にパブリックまたは信頼できないソースからの入力を使用して SQL ステートメントを作成する場合、 SQL インジェクション攻撃が可能になります。

テキストを連結するのではなく、パラメーターをバインドすることにより、 SQL インジェクション攻撃のリスクを最小限に抑えることができます。

バインドの例：

```javascript
let my_variable = 'variable' + '_value';
let statement = snowflake.createStatement({
    sqlText: 'INSERT INTO table2 (col1, col2) VALUES (?, ?);',
    binds: ['LiteralValue1', my_variable],
});
```

## 練習

ストアドプロシージャを何かと使う方法を学びました、今学んだ事を練習しましょう。
この練習で JavaScript, Python と SQL を利用し、同じ事をする三つのストアドプロシージャ作成します。

環境とタスクの説明：
次の事を想像してください。あなたは日本国内各県に複雑の店がある大きな小売会社で働いています。あなたの会社は良く色々な県で販売キャンペーンをやります。各店の店名と県名、販売キャンペーンが行おっているかないか、販売キャンペーンが行おっているば、割引のデータを保存するテーブルがあります。毎回会社ある県で販売キャンペーンが始めり、それとも、終了した時に、テーブルを更新するのは面倒くさいので、あなたはテーブルを更新するストアドプロシージャを開発したいです。

### データをの準備

キャンペーンテーブルを作成します。

```SQL
create table if not exists campaigns_table(
  id INT,
  store_name VARCHAR,
  prefecture VARCHAR,
  campaign BOOLEAN DEFAULT false,
  discount INT DEFAULT 0
);
```

キャンペーンテーブルにデータを入力します。

```SQL
INSERT INTO campaigns_table (id, store_name, prefecture)
VALUES
(1, 'Store A', 'Hokkaido'),
(2, 'Store B', 'Aomori'),
(3, 'Store C', 'Iwate'),
(4, 'Store D', 'Miyagi'),
(5, 'Store E', 'Akita'),
(6, 'Store F', 'Yamagata'),
(7, 'Store G', 'Fukushima'),
(8, 'Store H', 'Ibaraki'),
(9, 'Store I', 'Tochigi'),
(10, 'Store J', 'Gunma'),
(11, 'Store K', 'Saitama'),
(12, 'Store L', 'Chiba'),
(13, 'Store M', 'Tokyo'),
(14, 'Store N', 'Kanagawa'),
(15, 'Store O', 'Niigata');
```

<details>
<summary class="fancy">
もっとデータを入力したいなら、クリックしてください。
</summary>

```sql
INSERT INTO campaigns_table (id, store_name, prefecture)
VALUES
(16, 'Store P', 'Toyama'),
(17, 'Store Q', 'Ishikawa'),
(18, 'Store R', 'Fukui'),
(19, 'Store S', 'Yamanashi'),
(20, 'Store T', 'Nagano'),
(21, 'Store U', 'Gifu'),
(22, 'Store V', 'Shizuoka'),
(23, 'Store W', 'Aichi'),
(24, 'Store X', 'Mie'),
(25, 'Store Y', 'Shiga'),
(26, 'Store Z', 'Kyoto'),
(27, 'Store AA', 'Osaka'),
(28, 'Store AB', 'Hyogo'),
(29, 'Store AC', 'Nara'),
(30, 'Store AD', 'Wakayama'),
(31, 'Store AE', 'Tottori'),
(32, 'Store AF', 'Shimane'),
(33, 'Store AG', 'Okayama'),
(34, 'Store AH', 'Hiroshima'),
(35, 'Store AI', 'Yamaguchi'),
(36, 'Store AJ', 'Tokushima'),
(37, 'Store AK', 'Kagawa'),
(38, 'Store AL', 'Ehime'),
(39, 'Store AM', 'Kochi'),
(40, 'Store AN', 'Fukuoka'),
(41, 'Store AO', 'Saga'),
(42, 'Store AP', 'Nagasaki'),
(43, 'Store AQ', 'Kumamoto'),
(44, 'Store AR', 'Oita'),
(45, 'Store AS', 'Miyazaki'),
(46, 'Store AT', 'Kagoshima'),
(47, 'Store AU', 'Okinawa'),
(48, 'Store AV', 'Hokkaido'),
(49, 'Store AW', 'Aomori'),
(50, 'Store AX', 'Iwate'),
(51, 'Store AY', 'Miyagi'),
(52, 'Store AZ', 'Akita'),
(53, 'Store BA', 'Yamagata'),
(54, 'Store BB', 'Fukushima'),
(55, 'Store BC', 'Ibaraki'),
(56, 'Store BD', 'Tochigi'),
(57, 'Store BE', 'Gunma'),
(58, 'Store BF', 'Saitama'),
(59, 'Store BG', 'Chiba'),
(60, 'Store BH', 'Tokyo'),
(61, 'Store BI', 'Kanagawa'),
(62, 'Store BJ', 'Niigata'),
(63, 'Store BK', 'Toyama'),
(64, 'Store BL', 'Ishikawa'),
(65, 'Store BM', 'Fukui'),
(66, 'Store BN', 'Yamanashi'),
(67, 'Store BO', 'Nagano'),
(68, 'Store BP', 'Gifu'),
(69, 'Store BQ', 'Shizuoka'),
(70, 'Store BR', 'Aichi'),
(71, 'Store BS', 'Mie'),
(72, 'Store BT', 'Shiga'),
(73, 'Store BU', 'Kyoto'),
(74, 'Store BV', 'Osaka'),
(75, 'Store BW', 'Hyogo'),
(76, 'Store BX', 'Nara'),
(77, 'Store BY', 'Wakayama'),
(78, 'Store BZ', 'Tottori'),
(79, 'Store CA', 'Shimane'),
(80, 'Store CB', 'Okayama'),
(81, 'Store CC', 'Hiroshima'),
(82, 'Store CD', 'Yamaguchi'),
(83, 'Store CE', 'Tokushima'),
(84, 'Store CF', 'Kagawa'),
(85, 'Store CG', 'Ehime'),
(86, 'Store CH', 'Kochi'),
(87, 'Store CI', 'Fukuoka'),
(88, 'Store CJ', 'Saga'),
(89, 'Store CK', 'Nagasaki'),
(90, 'Store CL', 'Kumamoto'),
(91, 'Store CM', 'Oita'),
(92, 'Store CN', 'Miyazaki'),
(93, 'Store CO', 'Kagoshima'),
(94, 'Store CP', 'Okinawa'),
(95, 'Store CQ', 'Hokkaido'),
(96, 'Store CR', 'Aomori'),
(97, 'Store CS', 'Iwate'),
(98, 'Store CT', 'Miyagi'),
(99, 'Store CU', 'Akita'),
(100, 'Store CV', 'Yamagata'),
(101, 'Store CW', 'Fukushima'),
(102, 'Store CX', 'Ibaraki'),
(103, 'Store CY', 'Tochigi'),
(104, 'Store CZ', 'Gunma'),
(105, 'Store DA', 'Saitama'),
(106, 'Store DB', 'Chiba'),
(107, 'Store DC', 'Tokyo'),
(108, 'Store DD', 'Kanagawa'),
(109, 'Store DE', 'Niigata'),
(110, 'Store DF', 'Toyama'),
(111, 'Store DG', 'Ishikawa'),
(112, 'Store DH', 'Fukui'),
(113, 'Store DI', 'Yamanashi'),
(114, 'Store DJ', 'Nagano'),
(115, 'Store DK', 'Gifu'),
(116, 'Store DL', 'Shizuoka'),
(117, 'Store DM', 'Aichi'),
(118, 'Store DN', 'Mie'),
(119, 'Store DO', 'Shiga'),
(120, 'Store DP', 'Kyoto'),
(121, 'Store DQ', 'Osaka'),
(122, 'Store DR', 'Hyogo'),
(123, 'Store DS', 'Nara'),
(124, 'Store DT', 'Wakayama'),
(125, 'Store DU', 'Tottori'),
(126, 'Store DV', 'Shimane'),
(127, 'Store DW', 'Okayama'),
(128, 'Store DX', 'Hiroshima'),
(129, 'Store DY', 'Yamaguchi'),
(130, 'Store DZ', 'Tokushima'),
(131, 'Store EA', 'Kagawa'),
(132, 'Store EB', 'Ehime'),
(133, 'Store EC', 'Kochi'),
(134, 'Store ED', 'Fukuoka'),
(135, 'Store EE', 'Saga'),
(136, 'Store EF', 'Nagasaki'),
(137, 'Store EG', 'Kumamoto'),
(138, 'Store EH', 'Oita'),
(139, 'Store EI', 'Miyazaki'),
(140, 'Store EJ', 'Kagoshima'),
(141, 'Store EK', 'Okinawa'),
(142, 'Store EL', 'Hokkaido'),
(143, 'Store EM', 'Aomori'),
(144, 'Store EN', 'Iwate'),
(145, 'Store EO', 'Miyagi'),
(146, 'Store EP', 'Akita'),
(147, 'Store EQ', 'Yamagata'),
(148, 'Store ER', 'Fukushima'),
(149, 'Store ES', 'Ibaraki'),
(150, 'Store ET', 'Tochigi'),
(151, 'Store EU', 'Gunma'),
(152, 'Store EV', 'Saitama'),
(153, 'Store EW', 'Chiba'),
(154, 'Store EX', 'Tokyo'),
(155, 'Store EY', 'Kanagawa'),
(156, 'Store EZ', 'Niigata'),
(157, 'Store FA', 'Toyama'),
(158, 'Store FB', 'Ishikawa'),
(159, 'Store FC', 'Fukui'),
(160, 'Store FD', 'Yamanashi'),
(161, 'Store FE', 'Nagano'),
(162, 'Store FF', 'Gifu'),
(163, 'Store FG', 'Shizuoka'),
(164, 'Store FH', 'Aichi'),
(165, 'Store FI', 'Mie'),
(166, 'Store FJ', 'Shiga'),
(167, 'Store FK', 'Kyoto'),
(168, 'Store FL', 'Osaka'),
(169, 'Store FM', 'Hyogo'),
(170, 'Store FN', 'Nara'),
(171, 'Store FO', 'Wakayama'),
(172, 'Store FP', 'Tottori'),
(173, 'Store FQ', 'Shimane'),
(174, 'Store FR', 'Okayama'),
(175, 'Store FS', 'Hiroshima'),
(176, 'Store FT', 'Yamaguchi'),
(177, 'Store FU', 'Tokushima'),
(178, 'Store FV', 'Kagawa'),
(179, 'Store FW', 'Ehime'),
(180, 'Store FX', 'Kochi'),
(181, 'Store FY', 'Fukuoka'),
(182, 'Store FZ', 'Saga'),
(183, 'Store GA', 'Nagasaki'),
(184, 'Store GB', 'Kumamoto'),
(185, 'Store GC', 'Oita'),
(186, 'Store GD', 'Miyazaki'),
(187, 'Store GE', 'Kagoshima'),
(188, 'Store GF', 'Okinawa'),
(189, 'Store GG', 'Hokkaido'),
(190, 'Store GH', 'Aomori'),
(191, 'Store GI', 'Iwate'),
(192, 'Store GJ', 'Miyagi'),
(193, 'Store GK', 'Akita'),
(194, 'Store GL', 'Yamagata'),
(195, 'Store GM', 'Fukushima'),
(196, 'Store GN', 'Ibaraki'),
(197, 'Store GO', 'Tochigi'),
(198, 'Store GP', 'Gunma'),
(199, 'Store GQ', 'Saitama'),
(200, 'Store GR', 'Chiba');
```

</details>

</br>

---

### ストアドプロシージャを三つの言語で作りましょう

条件：現在は会社でキャンペーンが行おっていませんが、北海道でキャンペーンが始める予定です。

#### JavaScript

```JavaScript
let sql_cmd = "select * from table1 where year < 2016";
let statement = snowflake.createStatement({sqlText: sql_cmd});
let result_set = statement.execute();
```

- Snowflake の JavaScript ストアドプロシージャ環境では`snowflake`というオブジェクトは、宣言なしで存在する特別なオブジェクトです。オブジェクトは各ストアドプロシージャのコンテキスト内で提供され、 API を公開して、サーバーと対話できるようにします。つまり、SQL コードを実行するに、この`snowflake`オブジェクトを利用します。

- JavaScript を使用するストアドプロシージャの場合、ステートメントの SQL 部分の識別子（引数名など）は自動的に大文字に変換されます。

- Snowflake ストアドプロシージャの API は同期的です。

じゃあ、`campaigns_table`テーブルを更新するストアドプロシージャを作りましょう。

```JavaScript
CREATE OR REPLACE PROCEDURE TOGGLE_DISCOUNTS_JS(REGION STRING, ONCAMPAIGN BOOLEAN, DISCOUNT FLOAT DEFAULT 0)
RETURNS VARCHAR
LANGUAGE JAVASCRIPT
AS
$$
    if((ONCAMPAIGN && DISCOUNT <= 0) || (!ONCAMPAIGN && DISCOUNT != 0))
    {
      throw new Error('Input arguments are wrong');
    }
    const tableName = 'campaigns_table';
    const campaingColumn = 'CAMPAIGN';
    const discountColumn = 'DISCOUNT';
    const regionLowerCase = REGION.toLowerCase();
    const regionUpperCase = regionLowerCase.toUpperCase();
    const regionCapitilized = regionUpperCase.charAt(0) + regionLowerCase.substring(1);
   
    const statement = snowflake.createStatement({
      sqlText: `UPDATE ${tableName} SET ${campaingColumn} = :1, ${discountColumn} = :2 
                WHERE prefecture IN (:3, :4, :5, :6);`,
      binds:[ONCAMPAIGN, DISCOUNT, REGION, regionLowerCase, regionUpperCase, regionCapitilized]
      });
    statement.execute();
    return `${statement.getNumRowsUpdated()} 行が更新されました。`;
$$;

```

使う方：
もし、ある県で販売キャンペーンが始まった場合は、その県の県名、`TRUE`（キャンペーンが行おっていると言う意味）、と割引数字をストアドプロシージャに出します。

もし、販売キャンペーンが終わった場合は、その県の県名、と`FALSE`（キャンペーンが行おっていないと言う意味）をストアドプロシージャに出します。

このストアドプロシージャを呼ぶ時に県名を大き文字で書いても、小さ文字で書いても, 大文字と小文字を混ぜて書いても、問題なく動くようにしました。

今は Hokkaido でキャンペーン始まりました。
上のストアドプロシージャを呼んでください。

```SQL
CALL TOGGLE_DISCOUNTS_JS('HOKKAIDO', TRUE, 20);
```

上のストアドプロシージャを呼んだ後、テーブルが更新されたか、確認してみてください。

```SQL
SELECT *
FROM campaigns_table;
-- or
SELECT *
FROM campaigns_table
WHERE prefecture = 'Hokkaido';
```

#### Python

JavaScript ストアドプロシージャ環境では`snowflake`オブジェクトがあったように、python ストアドプロシージャ環境では`session`オブジェクトがあります。SQL コードを実行するに、この`session`オブジェクトを利用します。

JavaScript ストアドプロシージャと同じ結果を達成するストアドプロシージャを python でやってみましょう。

```python
CREATE OR REPLACE PROCEDURE toggle_discounts_py(region STRING, is_discounted STRING, discount NUMBER DEFAULT 0)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'main'
AS
$$
def main(session, region, is_discounted, discount = 0):
    if (is_discounted and discount <= 0) or (not is_discounted and discount != 0):
      raise Exception('Input arguments are wrong')
    table_name = 'campaigns_table'
    campaing_column = 'CAMPAIGN'
    discount_column = 'DISCOUNT'
    region_lower = region.lower()
    region_upper = region_lower.upper()
    region_capitilized = region_lower.capitalize()
    sql_command = f"UPDATE {table_name} SET {campaing_column} = :1, {discount_column} =:2 WHERE prefecture IN (:3, :4, :5, :6);"
    result = session.sql(sql_command, [is_discounted, discount, region, region_lower, region_upper, region_capitilized]).collect()
    return result[0]
$$;
```

今は Tokyo でもキャンペーンが始まりました。
上のストアドプロシージャを呼んでください。

```sql
CALL TOGGLE_DISCOUNTS_PY('Tokyo', TRUE, 10);
```

上のストアドプロシージャを呼んだ後、テーブルが更新されたか、確認してみてください。

```SQL
SELECT *
FROM campaigns_table;
-- or
SELECT *
FROM campaigns_table
WHERE prefecture = 'Tokyo';
```

##### Python のストアドプロシージャの強み

Python のストアドプロシージャは特に Pandas ようなライブラリを使って、データ分析する為に役に立ちます。

以下のクエリーから Snowflake で使える Python のライブラリリストをクエリー出来ます。

```SQL
select * from
information_schema.packages
where language = 'python';
```

#### Snowflake Scripting (SQL)

上のストアドプロシージャと同じ結果を達成するストアドプロシージャを SQL でやってみましょう。

```SQL
CREATE OR REPLACE PROCEDURE toggle_discount_sql(
    region STRING,
    is_discounted STRING,
    discount NUMBER DEFAULT 0)
RETURNS VARCHAR NOT NULL
LANGUAGE SQL
AS
$$
  DECLARE
  invalid_arguments EXCEPTION (-20003, 'Input arguments are wrong');
  BEGIN
  IF ((is_discounted and discount <= 0) or (not is_discounted and discount != 0) or (discount > 100)) THEN
    RAISE invalid_arguments;
  END IF;
  UPDATE campaigns_table
  SET CAMPAIGN = :is_discounted, DISCOUNT = :discount
  WHERE PREFECTURE IN (:region, UPPER(:region), LOWER(:region), INITCAP(:region));
  RETURN 'Rows Updated: ' || SQLROWCOUNT;
  END;
$$;
```

今は Tokyo でキャンペーンが終わりました。
上のストアドプロシージャを呼んでください。

```SQL
CALL toggle_discount_sql(
    REGION => 'ToKyO',
    is_discounted => FALSE
    );
```

上のストアドプロシージャを呼んだ後、テーブルが更新されたか、確認してみてください。

```SQL
SELECT *
FROM campaigns_table;
-- or
SELECT *
FROM campaigns_table
WHERE prefecture = 'Tokyo';
```

---

## 結論

ストアド プロシージャは強力な機能です。ハンドラ/ロジックは、さまざまな言語のいずれかで記述で、言語の選択に正しい選択や間違った選択はありません。どの言語に最も得意なら、その言語を使ってください。

Snowflake の機能についてもっと学びたいなら以下の記事をご覧ください。
