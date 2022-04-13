# cbpi4-TelegramPushNotifications
Telegram Push Notifications for Craftbeerpi 4

This Plugin allows you to interact with your craftbeerpi 4 instance.

Plugin Install:
1. run `pip install https://github.com/pascal1404/cbpi4-TelegramPushNotifications/archive/refs/heads/main.zip`
2. change directory to path where your local config-folder is. like `cd /home/pi/craftbeerpi`
3. run `cbpi add TelegramPushNotifications`
4. start your craftbeer 4 with ´cbpi start´

Setup:
1. Install this plugin from CBPI
2. Install Telegram app from [Telegram](https://telegram.org/)
3. Create Telegram Bot and acquire Bot token (also see: [Telegram-Doc](https://core.telegram.org/bots#6-botfather))
    * On Telegram, search `@BotFather`, send him a `/start` message
    * To create a new bot send him `/newbot` message and follow instructions to set up username and name for your new bot
    * BotFather will send you confirmation message with bot token. Save it for later
4. Get Chat ID
    * On Telegram, search your bot (by the username you just created) or by clicking on the link that BotFather gave you inside the bot creation confirmation message, press the “Start” button or send a `/start` message
    * Open a new tab with your browser, enter `https://api.telegram.org/bot<yourtoken>/getUpdates` , replace `<yourtoken>` with your API token, press enter and you should see something like this:
    ```{"ok":true,"result":[{"update_id":77xxxxxxx,"message":{"message_id":333,"from":{"id":34xxxxxxx,"is_bot":false,"first_name":"XXXX","last_name":"XXXX","username":"xxxxxxx","language_code":"en-GB"}```
    * Look for “id”, for instance, 34xxxxxxx above is my chat id. Look for yours and save it for later
    * If you cannot see your chat id, remove your bot from the chat and add it back (to remove click on three dots in the right corner and select delete conversation then add it back by searching for bot username or clicking the link in confirmation message from BotFather again). Open the url described above again and you should find you chat id.
5. Login to your Telegram account (https://my.telegram.org) with the phone number of your telegram account to use.
6. Click under API Development tools.
7. A Create new application window will appear. Fill in your application details. There is no need to enter any URL, and only the first two fields (App title and Short name) can currently be changed later.
8. Click on Create application at the end. 
> :warning: **_Attention:_** Remember that your API hash is secret and Telegram won’t let you revoke it. Don’t post it anywhere!

9. Input your Bot token, Chat ID, API ID and API HASH you acquired in previous steps into the Craftbeerpi parameters page (may require a system reboot if parameters not visible).
10. Reboot your system.
11. Everything should now be pushed to your Telegram.

In you Telegram-chat you have a menu with commands you can use. 
Notifications will be forwarded to Telegram.
Notifications with actions like MashIn-step-notification will get the text of the notification and the buttons. You can use the buttons in Telegram or in the dashboard, both works the same.

ToDo:
- [ ] send chart of Kettle or Fermenter as picture works for Influxdb-Cloud and CSV-logfiles should be added to influxdb v1.x
- [ ] send chart of Kettle or Fermenter as picture works for CSV-logfiles, but time-duration is not yet implemented.