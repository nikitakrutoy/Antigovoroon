import telepot
import sys
import os
# from server import TOKEN


TOKEN = os.environ["ANTIGOVOROON_TOKEN"]

action = sys.argv[1]
bot = telepot.Bot(TOKEN)
if action == "set":
    response = bot.setWebhook(
        url='https://nikitakrutoy.ml/antigovoroon/{bot_token}/'.format(bot_token=TOKEN))
    print(response)

if action == "info":
    response = bot.getWebhookInfo()
    print(response)
if action == "unset":
    res = bot.deleteWebhook()
    print(res)
    if res:
        print("Successfully deleted!")
    else:
        print("Error!")
