# -*- coding: utf-8 -*-
import json
import requests
import logging
import requests
import vk_api
import os
import json
import sqlite3 as lite
from vk_api import VkUpload
from utils.recognition import recognize
from vk_api.longpoll import VkLongPoll, VkEventType

logging.basicConfig(filename='logs/longpoll.log', level=logging.DEBUG)

logger = logging.getLogger()

login = os.environ["ANTIGOVOROON_LOGIN"]
password = os.environ["ANTIGOVOROON_PASSWORD"]


def method(method, values):
    http = requests.Session()
    return http.post(
        'https://api.vk.com/method/' + method,
        values
    ).text


def getUserToken(user_id):
    con = lite.connect("data/vk.db")
    with con:
        cur = con.cursor()
        query = "select access_token from Users where user_id={user_id}"
        cur.execute(query.format(user_id=user_id))
        access_token = cur.fetchall()
        return access_token[0][0]


def main():

    # Авторизация пользователя:
    session = requests.Session()
    vk_session = vk_api.VkApi(
        login=login,
        password=password,
        scope=131072+4096
    )
    # vk_session_temp = vk_api.VkApi(token=TOKEN)

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    # Авторизация группы:
    # # при передаче token вызывать vk_session.auth не нужно
    # vk_session = vk_api.VkApi(token=TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)



    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_token = getUserToken(event.user_id)
            logger.debug(event.raw)
            if "fwd" in event.attachments:
                fwd_messages = event.attachments["fwd"].split(",")
                for message in fwd_messages:
                    _, message_id = message.split("_")
                    vk.messages.getById()
            if "attach1" in event.attachments.keys():
                print(event.attachments)
                print(event.attachments["attach1"])
                owner_id, item_id = event.attachments["attach1"].split("_")
                print(event.attachments["attach1"])
                print(vk_session.token['access_token'])
                response = method(
                    method="docs.getById",
                    values={
                        "docs": event.attachments["attach1"],
                        "access_token": user_token,
                        "v": 5.71
                    },
                )
                print(response)
                url = json.loads(response)["response"][0]["preview"]["audio_msg"]["link_ogg"]
                print(url)
                res = requests.get(url)
                text = recognize(res.content, "ru-RU", "vk")
                vk.messages.send(
                    user_id=event.user_id,
                    message=text,
                )


            if event.text:
                vk.messages.send(
                            user_id=event.user_id,
                            message=event.text
                        )


if __name__ == '__main__':
    main()
