# Posting messages on Slack from Snowflake

Using Snowflake's NOTIFICATION INTEGRATION function and Slack's Webhooks feature it is possible to send messages to Slack from Snowflake.
This method can be used to send messages to Microsoft Teams and PagerDuty as well.

_If you are not familair with Slack, you can watch this [video][Slack_overview_en] to get a quick overview of Slack._

**Webhook** is a http request. It is API call sometimes called reverse API or Push API. The defining feature of webhook is that the client instructs the server to callback (send http request to) the client when some event happens.  
In our case, the client, slack app, instucts the Snowflake to call (make a http request to an url endpoint) when some kind of event happens. 

It is more about point of view: from which side you look at the process. 
From the Snowflake side, it is a regular API call, making a post request to Slack.
But from the Slack side it is webhook (reverse API call) i.e, asking Snowflake to callback when an event occurs at a specific endpoint. 

<br/>

## Steps:

### On Slack side
- Create a channel for testing purposes (optional)
- Create Slack app
- Integrate app to the channel
- Get app's webhook URL


1. #### Creating a channel for testing purposes (optional)
    1. Login to Slack, From Sidebar on the left click on "Add channels" button
       
        ![add channel](./images/add_channel.PNG)
        <br/>
    1. Enter channel name
        ![enter channel name](./images/channel_name.PNG)
        <br/>
    1. Choose channel visibility
        ![channel visibility](./images/channel_privacy.PNG)
        **public** channels are visible to everyone within the workspace.
        **private** channels are visible to people who are invited.
        <br/>
    1. Click on the "Create" button
    <br/>


1. #### Creating Slack App
    1. Open Slack Apps's [Dashboard page](https://api.slack.com/apps)
    <br/>
    1. Click on "Create App" button
    ![Create app image](./images/create_app.PNG)
    <br/>
    1. Select "From Scratch" option
    ![From Scrach](./images/from_scrach.PNG)
    <br/>
    1. Enter App name and choose Workspace from drop-down
    ![Enter Aoo name and choose workspace](./images/app_name_and_workspace.PNG)
    1. Click "Create App" button
    <br/>


1. ####  Integrating the app to the channel
    1.  On the App settings page, click "Incoming webhooks" link on the left sidebar
    ![incoming webhooks](./images/incoming_webhooks.PNG)
    _If you had closed the tab, you can find your app from [Slack app dashboard](https://api.slack.com/apps)_
    <br/>
    1. Toogle on "Activate Incoming Webhooks"
    ![Activate incoming webhook](./images/activate_incoming_webhook.PNG)
    <br/>
    1. Go to the bottom and click "Add New Webhook to Workspace" button
    ![Add New Webhook to Workspace](./images/add_new_workspace.PNG)
    <br/>
    1. Choose the channel you want to connect the app to and click "Allow" button
    ![select channel](./images/select_channel.PNG)
   <br/>
    After Integration on the channel you can see the new message confirming it
    ![app_integrated](./images/app_integrated.PNG)
    <br/>

1. #### Getting App's webhook URL
    On App's settings page Incoming Webhooks section go to bottom and copy "Webhook Url", we will use it soon. 
    ![Copy Webhook Url](./images/webhook_url.PNG)

__Note:__ App integration to a channel creates a unique Webhook Url for each channel。
What it means is that if you want to send messages to a different Slack channel from Snowflake, that channel should also be connected to the app and uniqly generated Webhook URL for that channel should be used on the Snowflake side.


---

### On Snowflake Side

1. #### Storing Webhook Url's token as a secret
    Necessary privileges：
    - Create secret
    - Read secret
    - Use secret
    <br/>

    Webhook Url looks like this： `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX`.
    We will store the token that comes after `https://hooks.slack.com/services/`part as a secret on Snowflake. 
    
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
    Necessary privileges：
    - CREATE INTEGRATION
    - USAGE On INTEGRATION

    <br/>

    ```SQL
    CREATE OR REPLACE NOTIFICATION INTEGRATION my_slack_webhook_int
    TYPE=WEBHOOK
    ENABLED=TRUE
    WEBHOOK_URL='https://hooks.slack.com/services/SNOWFLAKE_WEBHOOK_SECRET'
    WEBHOOK_SECRET=my_db.my_schema.my_slack_webhook_secret
    WEBHOOK_BODY_TEMPLATE='{"text": "SNOWFLAKE_WEBHOOK_MESSAGE"}'
    WEBHOOK_HEADERS=('Content-Type'='application/json');
    ```

    `SNOWFLAKE_WEBHOOK_SECRET`and`SNOWFLAKE_WEBHOOK_MESSAGE`は**placeholders** for a secret (in our case Webhook url token) and a message. 
  
  <br/>

1. #### NOTIFICATION INTEGRATIONを使う（呼ぶ）

 
    ```SQL
        CALL SYSTEM$SEND_SNOWFLAKE_NOTIFICATION(
            SNOWFLAKE.NOTIFICATION.TEXT_PLAIN(
                SNOWFLAKE.NOTIFICATION.SANITIZE_WEBHOOK_CONTENT('Hello Slack!')
            ),
            SNOWFLAKE.NOTIFICATION.INTEGRATION('my_slack_webhook_int')
        );
    ```

[`SNOWFLAKE.NOTIFICATION.SANITIZE_WEBHOOK_CONTENT`](https://docs.snowflake.com/en/sql-reference/functions/sanitize_webhook_content) removes placeholders (for example, the SNOWFLAKE_WEBHOOK_SECRET placeholder, which specifies a secret) from the body of a notification message to be sent.
If this function is not used and the message body contains a placeholder for a secret, then when a message is sent to a Slack webhook, a message containing a secret will be exposed to the Slack channel.

The rest are set functions to be used with NOTIFICATION INTEGRATION to send a message. 

##### Result

![final_result](./images/final_result.PNG)

<br/>

If calling 4 functions and stored procedures every time to send a message to a Slack is bothersome, a wrapper stored procedure can be used to simplify the process. 

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
#### Useful links：

- [creating Slack app](https://api.slack.com/quickstart)
- [Webhook urls on Slack](https://api.slack.com/messaging/webhooks)
- [Creating Webhook Notification on Snowflake](https://docs.snowflake.com/en/user-guide/notifications/webhook-notifications)

[Slack_overview_en]:https://www.youtube.com/watch?v=RRxQQxiM7AA
[Slack_overview_ja]:https://www.youtube.com/watch?v=cIDEPwOxQ2Y
