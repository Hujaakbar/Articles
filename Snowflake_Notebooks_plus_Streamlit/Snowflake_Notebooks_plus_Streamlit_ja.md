# Notebookの中でStreamlitを使う方法

SnowflakeでNotebookとStreamlitを使えるのを知っていますか？ Notebookの中でStreamlitを使えるのも知っていますか？もし、知らないなら、この記事を読んでください。
この記事でSnowflakeのNotebookの中でStreamlitを使え方法を説明します。

## NotebookとStreamlitは何でしょう？

Notebook
: ノートブックは、コードとその出力を 1 つのドキュメントに統合し、コード、説明文、視覚化、その他のリッチ メディアを組み合わせることができます。つまり、1 つのドキュメントで、コードを実行し、説明を追加し、出力を表示し、作業をより透明化することができます。
人気なのノートブックは[Jupyter Labs](https://jupyter.org/) と [Google Colab](https://colab.research.google.com/)です。

Snowflakeもノートブックをサポートしていますnので、Snowflakeのノートブックでは`Markdown`, `Python`と`SQL`コードを書けます。

![notebook_example](./images/notebook_example.PNG)

内部ノートブックは `.ipynb`. Interactive Python Notebook (インタラクティブ Python ノートブック) ファイル形式を使用します。

![Notebook Extention](./images/nb_extension.drawio.png)

**Notebookに加えて、SnowflakeがStreamlitもサポートしています。**

Streamlit
    : Streamlitを利用したら、Pythonだけを使ってインタラクティブなウェッブアプリを開発する為に使えます。
    つまり、HTML, JavaScript, CSSとかサーバサイドの言語とフレームワークの知識がなくてもStreamlitを使ってウェッブアプリを開発出来ます。
    [Streamlitの概要](https://streamlit.io/)

## Notebookの中でStreamlit

Notebookの中で[Streamlit](https://docs.streamlit.io/)を使う事が可能です。

**:warning: 注意点:**
> Notebookの中でStreamlitのコードを書き、実行するのは可能ですが、もう作成された別の場所であるStreamlitのアプリを呼ぶことが出来ないです。
>
> もしもう作成された別の場所であるStreamlitのアプリをNotebookの中で使いたいなら、そのStreamlitアプリのコードをコピーし、Notebookにpasteする必要があります。

Streamlitを使う為に、Streamlitと他の必要なライブラリを以下のように`import`する必要があります。

```python
import streamlit as st
```

StreamlitをNotebookで使って見ましょう！
以下のコードを実行してみてください。

```python
st.header('Streamlit is working!')
slider = st.slider(label='My Slider', min_value=0, max_value=10)
```

結果：

![python code1](./images/python1.PNG)

## Notebookではpythonセルが他のセルのデータをアクセ出来ます

他のセルのデータをアクセ出来為に、そのセルのセル名が必要です。
Snowflakeが自動的に`cell1`、`cell2`ようなセル名を生成します。\
`cell#`形も、`cells.cell#`形も使えます。

もっと進め前に、デモする為に使うデータの準備をしましょう。

`dummy_sales_table`と言うテーブルを作成します。

```SQL
create or replace table dummy_sales_table 
(ID integer, Region varchar, Sales integer);
```

このテーブルにデータを入力します。

```sql
insert into dummy_sales_table
values (1, 'China', 100),
 (2, 'Japan', 70), 
 (3, 'US', 120),
 (4, 'France', 30),
 (5, 'Germany', 90);
```

データの確認：

```sql
select * 
from dummy_sales_table;
```

![sql code1](./images/sql_code1.PNG)

このクエリーのセル名は`cell7`です。
このセル名を利用し、pythonのコードを確認してみましょう。

![python code](./images/python_code2.PNG)

クエリーの結果を直接に使えないです。使う前に、結果をいずれか`Pandas`の`DataFrame`オブジェクトか`Snowpark`の`DataFrame`オブジェクトに変える必要があります。

じゃあ、Streamlitを利用し、上のクエリーの結果からグラフを作成しましょう。

```python
# cell7の結果を Pandas dataframeに変える
my_df = cell7.to_pandas()

# Chart the data
st.subheader("Sales in 3 key countries")
st.bar_chart(data=my_df, x='REGION', y='SALES')
```

![python code 3](./images/python_code3.PNG)

## Python セルのデータをSQLセルで使う方法

 Python セルのデータをSQLセルで使う為に、variable名をSQLセルで `{{ variable名 }}`として書いてください。

![python code4](./images/python_code4.PNG)

### StreamlitセルのデータをSQLセルで使う方法

StreamlitはPythonライブラリので、Streamlitセルのデータを上にように、`{{ variable名 }}`、形を使って使います。

```python
table_name = st.selectbox(
    label='見たい例名を選択してください', 
    options=['dummy_sales_table', 'some_other_table']
    )

row_count = st.number_input(
    label='見たい行数を入力してください', 
    value=1, 
    min_value=1, 
    max_value=100
    )
```

結果：

![python code5](./images/python_code5.PNG)

もし、セルのコードじゃなくて、セルの結果だけを見たいなら、セルの上の右側にアル2番目のボタンを押してください。

![cell](./images/cell.drawio.png)

結果：

![python code6](./images/python_code6.PNG)

このStreamlitの`table_name`と`row_count`データをSQLクエリーで使いましょう。

```SQL
select * 
from {{ table_name }}
limit {{ row_count }};
```

結果：

![sql code2](./images/sql_code2.PNG)

Streamlitはインテラクティブなので、Streamlitのデータの価値が変わったら、Streamlitのセルから下にアル全てのセルが自動的に再実行されります。

![python_code7](./images/python_code7.PNG)
