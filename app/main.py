import os
import time
from typing import List

from app import mongo
from app import validator


import telebot
from flask import Flask, request
from dotenv import load_dotenv


load_dotenv(override=True)

TOKEN = os.environ["TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
SUPER_ADMIN = int(os.environ["SUPER_ADMIN"])
ADMIN_CACHE = {"super_admins":  [SUPER_ADMIN], "admins": []}

server = Flask(__name__)

categories = {
    "500": ["DAN", "EIE500", "EEE22", "CU2022"],
    "gen": ["CHAP", "AEIES", "CUMCH", "CUCHM", "CUMD", "CUSC"],
    "100": ["FRESH"],
    "200": ["CU2425"],
    "300": ["CU300"],
    "400": ["DAN", "EIE400"]
}


bot = telebot.TeleBot(TOKEN)
start_message_text = """Hi there \!\!\! 👋\n\nI'm CUSC bot 🤖, the official bot of the CU Student Council\.
I'm here to give you first hand information and news concerning student life on campus 🏫\.
You can also connect with the student council through the [official Instagram page](https://www.instagram.com/studentcouncil_cu/):\n\nStay tuned\!\!\! 💥
"""

admin_start_message = """
categories \= \{
    "500": ["DAN", "EIE500", "EEE22", "CU2022"],
    "gen": ["CHAP", "AEIES", "CUMCH", "CUCHM", "CUMD", "CUSC"],
    "100": ["FRESH"],
    "200": ["CU2425"],
    "300": ["CU300"],
    "400": ["DAN", "EIE400"]
    "all": \- Groups and DMs
    "private": \- Dms Only
\}

Example
```
/sendmedia
100,200,300
I am the CUSC Bot
photo
```
    This would send the a photo with the caption "I am the CUSC Bot" to "FRESH", "CU2425" and "CU300"

```
/sendmedia
all
Revalidation Form
document
```
    This would send the a file with the caption "Revalidation Form" to all groups and private users

**NOTE:**
    The "all" and "private" categories cannot be used with any other category
"""

message_dict = dict()


def is_admin(id: int) -> bool:
    """Returns true if a user is an admin or super admin
    """
    return (id in ADMIN_CACHE["admins"]) or (id in ADMIN_CACHE["super_admins"])


def is_super_admin(id: int):
    """Returns true if a user is a super admin
    """
    return id in ADMIN_CACHE["super_admins"]


def refresh_admin_cache():
    """Refreshes the local cache of the admins and super admins
    """

    all_admins = mongo.get_admins()
    regular_admins = filter(lambda x: x["role"] == "admin", all_admins)
    super_admins = filter(lambda x: x["role"] == "super_admin", all_admins)

    ADMIN_CACHE["admins"] = list(map(lambda x: x["chat_id"], regular_admins))
    ADMIN_CACHE["super_admins"] = list(
        map(lambda x: x["chat_id"], super_admins)).append(SUPER_ADMIN)


def send_messages(ids: List[str], func, **kwargs):
    message_dict.clear()
    count = 0
    for id in ids:
        try:
            message_object = func(id, **kwargs)
            count += 1
            message_dict[message_object.chat.id] = message_object.id
        except:
            continue
        if count % 20 == 0:
            time.sleep(.7)


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    chat = message.chat
    mongo.insert_new_user(chat.id, chat.type)

    if chat.type != "private":
        return

    if not is_admin(chat.id):
        bot.reply_to(message=message, text=start_message_text,
                     parse_mode="MarkdownV2")
        return

    bot.reply_to(message=message,
                 text=f"Hello {chat.first_name.split(' ')[0].title()},\n"+admin_start_message, parse_mode="MarkdownV2")


@bot.message_handler(commands=["deletemessage"])
def delete_messages(message):
    chat = message.chat
    if not is_admin(chat.id):
        return

    for chat_id, message_id in message_dict.items():
        bot.delete_message(chat_id=chat_id, message_id=message_id)


@bot.message_handler(commands=["add_admin"])
def add_admin(message):

    chat = message.chat
    if not is_super_admin(chat.id):
        return

    res = validator.validate_add_admin(message.text)
    errors = res["errors"]
    data = res["data"]

    if errors is not None:
        msg = "\n".join([f"{field} - {err[0]}"
                        for field, err in res["errors"].items()])
        bot.send_message(chat.id, msg)
        return

    mongo.add_new_admin(data["id"], data["name"], data["role"])

    bot.send_message(chat.id, f"{data['name']} is now a/an {data['role']}")

    # update admin cache
    refresh_admin_cache()


@bot.message_handler(func=lambda message: message.text.startswith("/sendmedia"))
def broadcast_photo(message):
    chat = message.chat

    if not is_admin(chat.id):
        return

    # Initialise items
    receivers = message.text.split('\n')[1].strip().lower()
    type = message.text.split('\n')[-1].strip().lower()
    media_id = mongo.get_media_id(type=type)

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[2:-1])

    if type == "photo":
        func = bot.send_photo
        kw_args = {
            "caption": message_text,
            "photo": media_id,
        }
    elif type == "document":
        func = bot.send_document
        kw_args = {
            "caption": message_text,
            "document": media_id,
        }

    # Broadcast to all users
    if receivers == "all":
        ids = mongo.get_ids()
        send_messages(ids, func, **kw_args)
        return

    # Broadcast to dms only
    if receivers == "private":
        ids = mongo.get_ids(chat_type="private")
        send_messages(ids, func, **kw_args)
        return

    # Broadcast to groups only
    if receivers == "groups":
        ids = mongo.get_ids(chat_type="supergroup")
        send_messages(ids, func, **kw_args)
        return

    # Get a list of receivers categories
    receivers_list = [reciever.strip() for reciever in receivers.split(",")]
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    # Broadcast Photo to all categories
    group_ids = mongo.get_group_ids(group_names)
    send_messages(group_ids, func, kw_args)


@bot.message_handler(func=lambda message: message.chat.id in ADMIN_CACHE["super_admins"])
def broadcast_message(message):
    # Get a list of receivers categories
    receivers = message.text.split('\n')[0].strip().lower()

    receivers_list = [reciever.strip() for reciever in receivers.split(",")]

    # Get message text
    message_text = '\n'.join(message.text.split('\n')[1:])

    # Broadcast to all users
    if receivers == "all":
        ids = mongo.get_ids()
        send_messages(ids, bot.send_message,
                      text=message_text)
        return

    # Broadcast to dms only
    if receivers == "private":
        ids = mongo.get_ids(chat_type="private")
        send_messages(ids, bot.send_message,
                      text=message_text)
        return

    # Broadcast to groups only
    if receivers == "groups":
        ids = mongo.get_ids(chat_type="supergroup")
        send_messages(ids, bot.send_message,
                      text=message_text)
        return

    # Broadcast to custom set of groups
    group_names = [
        group_name for item in receivers_list for group_name in categories[item]]

    group_ids = mongo.get_group_ids(group_names)
    send_messages(group_ids, bot.send_message,
                  text=message_text)


@bot.message_handler(content_types=["photo", "document"])
def save_new_media(message):
    chat = message.chat

    if not is_admin(chat.id):
        return

    if message.photo:
        media_id = message.photo[0].file_id
        type = "photo"
    elif message.document:
        type = "document"
        media_id = message.document.file_id
    mongo.change_media_id(media_id, type=type)


@server.route("/" + TOKEN, methods=["POST"])
def getMessage():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(WEBHOOK_URL + TOKEN)
    return "!", 200


if __name__ == "__main__":
    refresh_admin_cache()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
