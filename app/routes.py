import telebot
from flask import request, render_template, Blueprint
import os
from dotenv import load_dotenv
from .utils import (
    setup_user,
    CustomFormatter,
)
import logging

from .models import User, session, Message
from datetime import date

logging.basicConfig(level=logging.DEBUG, format="%(message)s")

for handler in logging.root.handlers:
    handler.setFormatter(CustomFormatter())

load_dotenv()

routes_blueprint = Blueprint("routes", __name__)

"""
TODO You dont need a message_handler for announcing documents, photos and messages only for receiving commands.
? Read https://chatgpt.com/c/674e700d-ca64-8011-b3dd-679bb154e332 for more info
"""

bot = telebot.TeleBot(os.getenv("BOT_API_KEY"))
webhook_url = os.getenv("WEBHOOK_URL")



@routes_blueprint.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    logging.info(data)

    text = data["message"]["text"]
    chat_id = data["message"]["chat"]["id"]

    setup_user(bot, chat_id, text)

    return {"ok": True}


@routes_blueprint.route("/announce", methods=["POST"])
def announce():
    message = ""

    college = request.form["colleges"].split(" ")[0]
    level = request.form["levels"].split(" ")[0]
    files = request.files
    data = request.form

    if not data["message"] and not files:
        return render_template('messages/failure.html', reason = "No message or file was sent")

    message = Message(
        message=data["message"],
        college=college,
        level=level,
        document_name=files["file"].filename if files else None,
        date = date.today()
    )
    session.add(message)
    session.commit()

    if college == "All":
        college = None

    if level == "All":
        level = None

    query = session.query(User)
    if college:
        query = query.filter(User.college == college)

    if level:
        query = query.filter(User.level == int(level))

    all_users = query.all()

    if files:
        uploaded_file = files["file"]
        file_name = uploaded_file.filename

        caption = file_name if not data["message"] else data["message"]

        if file_name.endswith(("jpg", "jpeg", "png")):

            for user in all_users:
                bot.send_photo(user, uploaded_file, caption)
                return render_template('messages/success.html')

        elif file_name.endswith(("docx", "pdf", "xlsx", "pptx")):

            for user in all_users:
                bot.send_document(
                    user,
                    uploaded_file.stream,
                    caption=caption,
                    visible_file_name=file_name,
                )

            return render_template('messages/success.html')

    for user in all_users:
        bot.send_message(user.chat_id, data["message"])
    

    return render_template('messages/success.html')


@routes_blueprint.route("/")
def index():
    return render_template("index.html")

@routes_blueprint.route("/messages", methods=["GET"])
def messages():
    messages = session.query(Message).all()
    return render_template("messages.html", messages=messages)

bot.remove_webhook()
bot.set_webhook(webhook_url)
