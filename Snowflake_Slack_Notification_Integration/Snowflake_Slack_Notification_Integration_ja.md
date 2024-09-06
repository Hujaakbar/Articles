# SnowflakeからSlackにメッセージを送る

SnowflakeのNOTIFICATION INTEGRATIONと言う機能とSlackのWebhookを利用しSnowflakeからSlackにメッセージを送る事が出来ます。
同じ方法を使って、SnowflakeからMicrosft TeamsとPagerDutyにもメッセージを送るのは可能です。

Slackの使う方の概要が必要なら、この[動画][Slack_overview_ja]を見てください。

**Webhook** は http リクエストです。これは API 呼び出しで、リバース API または Push API と呼ばれることもあります。Webhook の特徴は、何らかのイベントが発生したときにクライアントがサーバーにコールバック (http リクエストを送信) するように指示することです。
この場合、クライアントである Slack アプリは、何らかのイベントが発生したときに Snowflake にコール (URL エンドポイントに http リクエストを送信) するように指示します。

これは、プロセスをどちらの側から見るかという視点に関するものです。
Snowflake 側から見ると、これは通常の API 呼び出しであり、Slack への投稿リクエストを行います。
しかし、Slack 側から見ると、これは Webhook (リバース API 呼び出し) であり、特定のエンドポイントでイベントが発生したときに Snowflake にコールバックするように要求します。
<br/>

## ステップ

### Slack上で必要なステップ
- テストの為にチャネルを作る
- Slackでアプリを作る
- 作ったアプリをチャネルに導入
- アプリのwebhook URLを取る


1. #### テストの為にチャネルを作る
    1. Slackにロギンし、左側のsidebarから「Add channels」ボタンを押し
       
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


1. #### Slackでアプリを作る
    1. [アプリを作成するページ](https://api.slack.com/apps)を開く
        <br/>
    1. Create App ボタンを押し       
        ![Create app image](./images/create_app.PNG)
       <br/>
    1. From Scratch オプションを選択       
        ![From Scrach](./images/from_scrach.PNG)
        <br/>
    1. アプリ名を入力しWorkspaceを選択       
        ![Enter Aoo name and choose workspace](./images/app_name_and_workspace.PNG)
    1. Create App ボタンを押し
        <br/>


1. #### Slackアプリをチャネルに導入
    1.  アプリの設定ページの左側にある「Incoming webhooks」を押し
       
        ![incoming webhooks](./images/incoming_webhooks.PNG)
       
        _作ったアプリのページを見つけれないなら、アプリdashbordに行ってください。_
       
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

1. #### アプリのwebhook URLを取る
    アプリをチャネルに導入/繋ぐ後に、アプリの設定ページに戻ってきます。
    アプリの設定ページのIncoming Webhooksセクションの下に
    作成された「Webhook Url」をコピーしてください。
   
    ![Copy Webhook Url](./images/webhook_url.PNG)

    __Note:__ 各チャネルは自分の特別な Webhook Urlがあります。
    と言うのは、テストの後に、アプリを本当のチャネルに導入したら、そのチャネルのWebhook Urlを使うべきです。




---

### Snowflake上で必要なステップ

1. #### WebhookのトケンをSecretとして保存
    必要な権限：
    - secretをcreate
    - secretをread
    - secretをuse
    <br/>

    SlackのWebhook Urlはこのような形です： `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`。
    `https://hooks.slack.com/services/`の後の部分をSnowflakeでsecretとして保存します。
    
    <br/>

    ```SQL
    CREATE OR REPLACE SECRET my_slack_webhook_secret
    TYPE = GENERIC_STRING
    SECRET_STRING = 'T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX';
    ```
    <br/>

    ![create secret](./images/secret_created.PNG)

    <br/>

1. #### NOTIFICATION INTEGRATIONを作成
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

    `SNOWFLAKE_WEBHOOK_SECRET`と`SNOWFLAKE_WEBHOOK_MESSAGE`はsecretとメッセージの**プレースホルダー**です。
  
      <br/>

1. #### NOTIFICATION INTEGRATIONを使う（呼ぶ）

 
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
    
    残りの関数は、NOTIFICATION INTEGRATIONを使用してメッセージを送信するために使用される設定関数です。
    
    ##### 結果
    
    ![final_result](./images/final_result.PNG)
    
    <br/>
    
    もし上のように4つのStored Procedureと関数を使ってNOTIFICATION INTEGRATIONを呼ぶ事をもっと簡単にしたいなら、wrapper Stored Procedureを作成出来ます。
    
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
#### 役に立つリンク：

- [Slackでアプリを作る](https://api.slack.com/quickstart)
- [SlackでWebhook url を作る](https://api.slack.com/messaging/webhooks)
- [Webhook NotificationをSnowflakeで作成](https://docs.snowflake.com/en/user-guide/notifications/webhook-notifications)

[Slack_overview_en]:https://www.youtube.com/watch?v=RRxQQxiM7AA
[Slack_overview_ja]:https://www.youtube.com/watch?v=cIDEPwOxQ2Y
