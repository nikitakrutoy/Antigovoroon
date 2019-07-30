import telepot
import requests
import os
from pydub import AudioSegment
from utils.recognition import recognize
from time import time, sleep
from concurrent.futures import ThreadPoolExecutor

TOKEN = os.environ["ANTIGOVOROON_TOKEN"]
Bot = telepot.Bot(TOKEN)

recognizedMsg = "<b>{username}</b> сказал(а):\n"


def getVoiceDataLink(fileId):
    link = "https://api.telegram.org/file/bot{0}/{1}"
    filePath = Bot.getFile(fileId)["file_path"]
    return link.format(TOKEN, filePath)
    # response = requests.get(link.format(TOKEN, filePath))


def changeSampleRate(raw):
    audio = AudioSegment(raw)
    audio.set_frame_rate(16000)
    return audio.raw_data


def loadingUI(future, chat_id, sent_msg):
    k = 0
    while not future.done():
        msg = "Recognizing" + "." * (k % 4)
        Bot.editMessageText((chat_id, sent_msg["message_id"]), msg)
        sleep(0.2)
        k += 1


def getUserName(user):
    if "first_name" in user.keys():
        return user["first_name"] + " " + user["last_name"]
    if "username" in user.keys():
        return user["username"]


def handle(message):
    content_type, chat_type, chat_id = telepot.glance(message)
    # Bot.sendMessage(chat_id, "Message recieved")
    username = getUserName(message["from"])
    if content_type == "voice":
        voice = message["voice"]
        link = getVoiceDataLink(voice["file_id"])
        response = requests.get(link)
        sent_msg = Bot.sendMessage(chat_id, "Recognizing...")

        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(recognize, response.content, "ru-RU", "tg")

        # loadingUI(future, chat_id, sent_msg)
        msg = future.result()
        if msg != "Could not recognize" and "group" in chat_type:
            msg = recognizedMsg.format(username=username) + msg

        Bot.editMessageText(
            (chat_id, sent_msg["message_id"]),
            msg,
            parse_mode="HTML"
        )


# For local testing
def server():
    last_update = 0
    while True:
        updates = Bot.getUpdates()
        if len(updates) != last_update:
            new_update = updates[-1]
            handle(new_update['message'])
        last_update = len(updates)


if __name__ == "__main__":
    server()
