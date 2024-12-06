import telebot
from flask import request, jsonify, render_template, Blueprint
import os
from dotenv import load_dotenv
from .utils import (
    extract_photo_info,
    extract_document_info,
    parse_message,
    ParseError,
    CustomFormatter,
)
import logging

from .models import User, session

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
sample_chat_id = os.getenv("SAMPLE_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")


@bot.message_handler(commands=["start"])
def send_start_message(message: telebot.types.Message):
    if message.text.startswith("/start"):
        logging.info("the /start command is being called")

        try:
            current_user = (
                session.query(User).filter_by(chat_id=message.chat.id).first()
            )
            if current_user:
                bot.send_message(
                    message.chat.id,
                    "You are already a verified user",
                )
                return
            new_user = User(chat_id=message.chat.id)
            session.add(new_user)
            session.commit()
            bot.send_message(
                message.chat.id,
                "Hi there, you want to receive updates from the CUSC announcement bot right? \n Just enter your College and Level to verify your studentship like this: \n \n CMSS 200",
            )
        except Exception as e:
            logging.error(e)

        logging.info("New user created")


@bot.message_handler(func=lambda message: True)
def send_user_info(message: telebot.types.Message):
    user = session.query(User).filter_by(chat_id=message.chat.id).first()
    if not user:
        bot.reply_to(
            message,
            "You are not a recorded user. \n please run the /start command to record yourself",
        )
    if user.college and user.level:
        bot.reply_to(
            message, "Please your college and level have been recorded already"
        )
        return
    values = None
    try:
        values = parse_message(message.text)
    except ParseError as error:
        bot.send_message(message.chat.id, str(error))
        logging.error(error)

    if values:
        user.college = values[0]
        user.level = values[1]
        session.commit()
        logging.info(
            f"User {user.chat_id} has been updated with {values[0]} and {values[1]}"
        )
        bot.send_message(message.chat.id, "You have been successfully verified")


@routes_blueprint.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    bot.process_new_updates([telebot.types.Update.de_json(data)])

    return {"ok": True}


@routes_blueprint.route("/announce", methods=["POST"])
def announce():
    message = ""

    college = request.form["colleges"].split(" ")[0]
    level = request.form["levels"].split(" ")[0]
    files = request.files
    data = request.form

    if not data["message"] and not files:
        return jsonify({"message": "No data sent"})

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
        uploaded_file = request.files["file"]

        file_name = uploaded_file.filename

        caption = files["file"].filename if not data["message"] else data["message"]

        if file_name.endswith(("jpg", "jpeg", "png")):
            photo_file, photo_width, photo_height = extract_photo_info(uploaded_file)

            for user in all_users:
                bot.send_photo(
                    user.chat_id,
                    photo_file,
                    caption=caption,
                )
                logging.info(f"Photo sent to {user.chat_id}")
                photo_file, photo_width, photo_height = extract_photo_info(
                    uploaded_file
                )
            return {"Message": "ok"}

        elif file_name.endswith(("docx", "pdf", "xlsx", ".pptx")):

            document = extract_document_info(uploaded_file)
            for user in all_users:
                bot.send_document(user.chat_id, document, caption=caption)
                document = extract_document_info(uploaded_file)

            return {"Message": "ok"}

    if data:
        for user in all_users:
            bot.send_message(user.chat_id, data["message"])

    return jsonify({message: "ok"})


@routes_blueprint.route("/")
def index():
    return render_template("index.html")


bot.remove_webhook()
bot.set_webhook(webhook_url)
