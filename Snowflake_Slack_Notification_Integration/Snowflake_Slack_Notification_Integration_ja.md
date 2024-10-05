# ワークフローの合理化：Snowflake アラートを Slack に送信する

![Snowflake](https://github.com/Hujaakbar/Articles/raw/main/Snowflake_Slack_Notification_Integration/images/snowflake.jpg)

Snowflake と Slack の連携でデータエンジニアの仕事がはかどる！
Snowflake と Slack を連携させると、データエンジニアの業務効率が大幅に向上します。\
その理由を見ていきましょう。

- **リアルタイムなエラー検知とデバッグ**: これまでのようにログを常に監視しなくても、Snowflake でエラーが発生した場合に Slack チャンネルに自動通知を送信するように設定できます。これは、コードのエラーを監視し、すぐに知らせてくれる専任のアシスタントがいるようなものです。迅速な問題解決が可能になります。これは、Webhook を使用することで実現します。Webhook とは、イベントをトリガーとして Snowflake から Slack に送信される自動 HTTP リクエストです。

- **チーム全体の情報共有**: Slack 連携により、データパイプラインなどの処理状況をチーム全体に共有することもできます。パイプラインが完了、失敗、または問題が発生した場合に、共有チャンネルに通知を送信するように Snowflake を設定できます。これにより、全員が状況を把握できるようになり、不要な進捗確認会議を減らすことができます。
この連携により、Slack がデータワークフロー管理の強力なハブとなり、データエンジニアの業務をよりシンプルかつ生産的にします。

## SnowflakeとSlackを統合する方法

Snowflake の NOTIFICATION INTEGRATION と言う機能と Slack の Webhook を利用し Snowflake から Slack にメッセージを送る事が出来ます。
同じ方法を使って、Snowflake から Microsoft Teams と PagerDuty にもメッセージを送るのは可能です。

Slack の使う方の概要が必要なら、この[動画][Slack_overview_ja]を見てください。

**Webhook** は http リクエストです。これは API 呼び出しで、リバース API または Push API と呼ばれることもあります。Webhook の特徴は、何らかのイベントが発生したときにクライアントがサーバーにコールバック (http リクエストを送信) するように指示することです。
この場合、クライアントである Slack アプリは、何らかのイベントが発生したときに Snowflake にコール (URL エンドポイントに http リクエストを送信) するように指示します。

これは、プロセスをどちらの側から見るかという視点に関するものです。
Snowflake 側から見ると、これは通常の API 呼び出しであり、Slack への投稿リクエストを行います。
しかし、Slack 側から見ると、これは Webhook (リバース API 呼び出し) であり、特定のエンドポイントでイベントが発生したときに Snowflake にコールバックするように要求します。

## ステップ

### Slack 上で必要なステップ

-   テストの為にチャネルを作る
-   Slack でアプリを作る
-   作ったアプリをチャネルに導入
-   アプリの webhook URL を取る

1. #### テストの為にチャネルを作る

    1. Slack にロギンし、左側の sidebar から「Add channels」ボタンを押し

        ![add channel](./images/add_channel.PNG)
        <br/>

    1. チャネル名を入力

        ![enter channel name](./images/channel_name.PNG)
        <br/>

    1. チャンネルの公開範囲は公開か非公開か決める

        ![channel visibility](./images/channel_privacy.PNG)
        <br/>

    1. 「Create」ボタンを押し
       <br/>

1. #### Slack でアプリを作る

    1. [アプリを作成するページ](https://api.slack.com/apps)を開く
       <br/>
    1. Create App ボタンを押し

        ![Create app image](./images/create_app.PNG)
        <br/>

    1. From Scratch オプションを選択

        ![From Scrach](./images/from_scrach.PNG)
        <br/>

    1. アプリ名を入力し Workspace を選択

        ![Enter Aoo name and choose workspace](./images/app_name_and_workspace.PNG)
        <br/>

    1. Create App ボタンを押し
       <br/>

1. #### Slack アプリをチャネルに導入

    1. アプリの設定ページの左側にある「Incoming webhooks」を押し

        ![incoming webhooks](./images/incoming_webhooks.PNG)

        _作ったアプリのページを見つけれないなら、アプリ dashbord に行ってください。_

        _リンク： [Slack app dashboard](https://api.slack.com/apps)_
        <br/>

    1. 「Activate Incoming Webhook」をトグルしてください。

        ![Activate incoming webhook](./images/activate_incoming_webhook.PNG)
        <br/>

    1. 一番下にある[Add New Webhook to Workspace]ボタンを押してください

        ![Add New Webhook to Workspace](./images/add_new_workspace.PNG)
        <br/>

    1. 導入したいチャネルを選択し、「Allow」ボタンを押してください

        ![select channel](./images/select_channel.PNG)
        <br/>
        アプリをチャネルに導入した後に、チャネルに確認のメッセージが来る

        ![app_integrated](./images/app_integrated.PNG)
        <br/>

1. #### アプリの webhook URL を取る

    アプリをチャネルに導入/繋ぐ後に、アプリの設定ページに戻ってきます。
    アプリの設定ページの Incoming Webhooks セクションの下に
    作成された「Webhook Url」をコピーしてください。

    ![Copy Webhook Url](./images/webhook_url.PNG)

    **Note:** 各チャネルは自分の特別な Webhook Url があります。
    と言うのは、テストの後に、アプリを本当のチャネルに導入したら、そのチャネルの Webhook Url を使うべきです。

---

### Snowflake 上で必要なステップ

1. #### Webhook のトケンを Secret として保存

    必要な権限：

    - secret を create
    - secret を read
    - secret を use
      <br/>

    Slack の Webhook Url はこのような形です： `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`。
    `https://hooks.slack.com/services/`の後の部分を Snowflake で secret として保存します。

    <br/>

    ```SQL
    CREATE OR REPLACE SECRET my_slack_webhook_secret
    TYPE = GENERIC_STRING
    SECRET_STRING = 'T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX';
    ```

    <br/>

    ![create secret](./images/secret_created.PNG)

    <br/>

1. #### NOTIFICATION INTEGRATION を作成

    必要な権限：

    - CREATE INTEGRATION
    - USAGE On INTEGRATION

    <br/>

    ```SQL
    CREATE OR REPLACE NOTIFICATION INTEGRATION my_slack_webhook_int
    TYPE=WEBHOOK
    ENABLED=TRUE
    WEBHOOK_URL='https://hooks.slack.com/services/SNOWFLAKE_WEBHOOK_SECRET'
    WEBHOOK_SECRET=my_secrets_db.my_secrets_schema.my_slack_webhook_secret
    WEBHOOK_BODY_TEMPLATE='{"text": "SNOWFLAKE_WEBHOOK_MESSAGE"}'
    WEBHOOK_HEADERS=('Content-Type'='application/json');
    ```

    `SNOWFLAKE_WEBHOOK_SECRET`と`SNOWFLAKE_WEBHOOK_MESSAGE`は secret とメッセージの**プレースホルダー**です。

      <br/>

1. #### NOTIFICATION INTEGRATION を使う（呼ぶ）

    ```SQL
    CALL SYSTEM$SEND_SNOWFLAKE_NOTIFICATION(
        SNOWFLAKE.NOTIFICATION.TEXT_PLAIN(
            SNOWFLAKE.NOTIFICATION.SANITIZE_WEBHOOK_CONTENT('my message')
        ),
        SNOWFLAKE.NOTIFICATION.INTEGRATION('my_slack_webhook_int')
    );
    ```

    [`SNOWFLAKE.NOTIFICATION.SANITIZE_WEBHOOK_CONTENT`](https://docs.snowflake.com/en/sql-reference/functions/sanitize_webhook_content)関数は送信される通知メッセージの本文からプレースホルダー (たとえば、シークレットを指定する SNOWFLAKE_WEBHOOK_SECRET プレースホルダー) を削除します。
    この関数が使用されず、メッセージ本文にシークレットのプレースホルダーが含まれている場合、メッセージが Slack Webhook に送信されると、シークレットを含むメッセージが Slack チャネルに投稿される可能性があります。

    残りの関数は、NOTIFICATION INTEGRATION を使用してメッセージを送信するために使用される設定関数です。

## 結果

![final_result](./images/final_result.PNG)

<br/>

もし上のように 4 つの Stored Procedure と関数を使って NOTIFICATION INTEGRATION を呼ぶ事をもっと簡単にしたいなら、wrapper Stored Procedure を作成出来ます。

例：

```SQL
CREATE OR REPLACE PROCEDURE post_on_slack(message)
RETURNS FLOAT
LANGUAGE SQL
AS
BEGIN
    CALL SYSTEM$SEND_SNOWFLAKE_NOTIFICATION(
        SNOWFLAKE.NOTIFICATION.TEXT_PLAIN(
            SNOWFLAKE.NOTIFICATION.SANITIZE_WEBHOOK_CONTENT(message)
        ),
        SNOWFLAKE.NOTIFICATION.INTEGRATION('my_slack_webhook_int')
    );
END;

Call post_on_slack('Hello Slack!')
```

---

### 役に立つリンク

-   [Slack でアプリを作る](https://api.slack.com/quickstart)
-   [Slack で Webhook url を作る](https://api.slack.com/messaging/webhooks)
-   [Webhook Notification を Snowflake で作成](https://docs.snowflake.com/en/user-guide/notifications/webhook-notifications)

[Slack_overview_en]: https://www.youtube.com/watch?v=RRxQQxiM7AA
[Slack_overview_ja]: https://www.youtube.com/watch?v=cIDEPwOxQ2Y
