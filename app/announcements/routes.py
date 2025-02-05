import telebot
from flask import request, render_template
import os
from dotenv import load_dotenv
from ..utils.utils import setup_user, CustomFormatter, mass_send_document, mass_send_photos
import logging
from app.models import add_message, filter_users, get_messages
from . import announcements


logging.basicConfig(level=logging.DEBUG, format="%(message)s")

for handler in logging.root.handlers:
    handler.setFormatter(CustomFormatter())

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_API_KEY"))
webhook_url = os.getenv("WEBHOOK_URL")


announcements.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    logging.info(data)

    if data.get("message"):
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

    if data.get("edited_message"):
        text = data["edited_message"]["text"]
        chat_id = data["edited_message"]["chat"]["id"]

    setup_user(bot, chat_id, text)

    return {"ok": True}


announcements.route("/announce", methods=["POST"])
def announce():
    college = request.form["colleges"].split(" ")[0]
    level = request.form["levels"].split(" ")[0]
    files = request.files
    data = request.form

    if not data["message"] and not files:
        return render_template(
            "messages/failure.html", reason="No message or file was sent"
        )

    add_message(data["message"], college, level)

    all_recipients = filter_users(college, level).data
    if files:
        uploaded_file = files["file"]
        file_name = uploaded_file.filename

        caption = file_name if not data["message"] else data["message"]

        if file_name.endswith(("jpg", "jpeg", "png")):
            mass_send_photos(all_recipients, bot, uploaded_file.stream, )

        elif file_name.endswith(("docx", "pdf", "xlsx", "pptx")):
            mass_send_document(
                all_recipients,
                bot,
                uploaded_file.stream,
                filename=uploaded_file.filename,
                caption = caption
            )

            return render_template("messages/success.html")

    for user in all_recipients:
        bot.send_message(user["chat_id"], data["message"])

    return render_template("messages/success.html")


announcements.route("/")
def index():
    return render_template("index.html")


announcements.route("/messages", methods=["GET"])
def messages():
    messages = get_messages()
    return render_template("messages.html", messages=messages)


bot.remove_webhook()
bot.set_webhook(webhook_url)
