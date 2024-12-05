import telebot
from flask import request, jsonify, render_template, Blueprint
import os
from dotenv import load_dotenv
from .utils import extract_photo_info, extract_document_info
import logging

from .models import User
from . import db

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

routes_blueprint = Blueprint("routes", __name__)

"""
TODO You dont need a message_handler for announcing documents, photos and messages only for receiving commands.
? Read https://chatgpt.com/c/674e700d-ca64-8011-b3dd-679bb154e332 for more info
"""

bot = telebot.TeleBot(os.getenv("BOT_API_KEY"))
sample_chat_id = os.getenv("SAMPLE_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")


@bot.message_handler(func=lambda message: True)
def send_message(message: telebot.types.Message):
    logging.debug("/start message handler is being called")
    if message.text.startswith("/start"):
        # new_user = User(chat_id=message.chat.id)
        # db.session.add(new_user)
        # db.session.commit()
        bot.send_message(
            message.chat.id,
            "Hi there, you want to receive updated from the CUSC announcement bot right? \n Just enter your College and Level to verify your studentship like this: \n \n CMSS 200",
        )


@routes_blueprint.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    bot.process_new_updates([telebot.types.Update.de_json(data)])

    return {"ok": True}


@routes_blueprint.route("/announce", methods=["POST"])
def announce():
    message = ""

    # * Dealing with file types
    files = request.files
    data = request.form

    if files:
        uploaded_file = request.files["file"]

        file_name = uploaded_file.filename

        caption = files["file"].filename if not data["message"] else data["message"]

        if file_name.endswith(("jpg", "jpeg", "png")):
            photo_file, photo_width, photo_height = extract_photo_info(uploaded_file)

            bot.send_photo(
                sample_chat_id,
                photo_file,
                caption=caption,
            )
            return {"Message": "ok"}

        elif file_name.endswith(("docx", "pdf", "xslx", ".pptx")):

            document = extract_document_info(uploaded_file)
            bot.send_document(sample_chat_id, document, caption=caption)
            return {"Message": "ok"}

    bot.send_message(sample_chat_id, data["message"])

    return jsonify({message: "ok"})


@routes_blueprint.route("/")
def index():
    return render_template("index.html")


bot.remove_webhook()
bot.set_webhook(webhook_url)
