from flask import Flask, request, make_response
from server import handle
from time import sleep
import os
import sqlite3 as lite
import logging
import requests

TOKEN = os.environ["ANTIGOVOROON_TOKEN"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
app = Flask(__name__)
passer = Flask(__name__)


# Activating environment
# activate_this = '/path/to/env/bin/activate_this.py'
# with open(activate_this) as file_:
#     exec(file_.read(), dict(__file__=activate_this))
# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='logs/server.log', level=logging.DEBUG)

logger = logging.getLogger()


@passer.route("/antigovoroon/<recieved_token>/", methods=['POST', 'GET'])
def handleTgRequestPass(recieved_token):
    sleep(2)
    return "foo"


@app.route("/antigovoroon/vk/get_access_token", methods=['POST', 'GET'])
def getVkAccessToken():
    code = request.args.get('code')
    redirect_uri = "https://oauth.vk.com/authorize?client_id=5798601&redirect_uri=https://nakrutoy.gq/antigovoroon/vk/get_access_token&display=page&scope=docs&response_type=code&v=5.71"
    client_id = CLIENT_ID
    client_secret = CLIENT_SECRET
    r = requests.get(
        'https://oauth.vk.com/access_token?client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={code}'.format(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=redirect_uri,
            code=code,
        )
    )
    data = r.json()
    # logger.debug(data)
    token = data["access_token"]
    # logger.debug(token)
    user_id = data["user_id"]
    con = lite.connect("data/vk.db")
    with con:
        cur = con.cursor()
        query1 = "select exists(select access_token from Users where user_id={user_id} limit 1);"
        query2 = "INSERT INTO Users(user_id, access_token) VALUES ({user_id}, \"{access_token}\");"
        query3 = "UPDATE Users SET access_token=\"{access_token}\" WHERE user_id={user_id};"
        logger.debug(query1.format(user_id=user_id, access_token=token))
        cur.execute(query1.format(user_id=user_id))
        is_exist = cur.fetchall()[0][0]
        if is_exist:
            cur.execute(query3.format(user_id=user_id, access_token=token))
        else:
            cur.execute(query2.format(user_id=user_id, access_token=token))
    return "Nice work, pal!"


@app.route("/antigovoroon/<recieved_token>/", methods=['POST', 'GET'])
def handleTgRequest(recieved_token):
    logger.debug("Request is recieved")
    if recieved_token == TOKEN and request.method == "POST":
        data = request.get_json()
        #logger.debug(data)
        if "message" in data.keys():
            handle(data["message"])
    return "foo"


@app.route("/test/")
def testServer():
    return "<h1 style='color:blue'>Hello World</h1>"
