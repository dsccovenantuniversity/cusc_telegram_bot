import telebot
from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import json
from utils import extract_photo_info, extract_document_info
import logging
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

"""
TODO You dont need a message_handler for announcing documents, photos and messages only for receiving commands.
? Read https://chatgpt.com/c/674e700d-ca64-8011-b3dd-679bb154e332 for more info
"""

bot = telebot.TeleBot(os.getenv("BOT_API_KEY"))
sample_chat_id = os.getenv("SAMPLE_CHAT_ID")
webhook_url = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy(app)


# * Models
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(255), unique=True, nullable=False)
    college = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.chat_id}>"


def load_template_json():
    with open("app/template_message.json") as f:
        return json.load(f)


@bot.message_handler(func=lambda message: True)
def send_message(message: telebot.types.Message):
    if message.text.startswith("/start"):
        new_user = User(chat_id=message.chat.id)
        db.session.add(new_user)
        db.session.commit()
        bot.send_message(
            message.chat.id,
            "Hi there, you want to receive updated from the CUSC announcement bot right? \n Just enter your College and Level to verify your studentship like this: \n \n CMSS 200",
        )


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    bot.process_new_updates([telebot.types.Update.de_json(data)])

    return {"ok": True}


@app.route("/announce", methods=["POST"])
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
            return

        elif file_name.endswith(("docx", "pdf", "xslx", ".pptx")):

            document = extract_document_info(uploaded_file)
            bot.send_document(sample_chat_id, document, caption=caption)
            return

    bot.send_message(sample_chat_id, data["message"])

    # update = telebot.types.Update.de_json(template_json)
    # bot.process_new_updates([update])

    return jsonify({message: "ok"})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(webhook_url)
    app.run(port=5000, debug=True)
