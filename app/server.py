import telebot
from flask import Flask, request, jsonify, render_template
import os
from dotenv import load_dotenv
import json
from utils import extract_photo_info, extract_document_info
from telebot.types import InputFile

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_API_KEY"))
bot.set_webhook("https://dirty-bats-eat.loca.lt/webhooks")

app = Flask(__name__)


def load_template_json():
    with open("app/template_message.json") as f:
        return json.load(f)


@bot.message_handler(content_types=["document"])
def send_document(message: telebot.types.Message):
    bot.send_document(
        "5588640228",
        InputFile(message.document.file_id),
        caption=message.caption,
    )


@bot.message_handler(content_types=["photo"])
def send_photo(message: telebot.types.Message):
    bot.send_photo(
        "5588640228",
        InputFile(message.photo[-1].file_id),
        caption=message.caption,
    )


@bot.message_handler(func=lambda message: True)
def send_message(message: telebot.types.Message):
    bot.send_message("5588640228", message.text)


@app.route("/webhooks", methods=["POST"])
def webhook():
    message = ""

    # * Dealing with file types
    files = request.files
    data = request.form

    template_json = load_template_json()

    if files:
        uploaded_file = request.files["file"]

        file_name = uploaded_file.filename

        if file_name.endswith(("jpg", "jpeg", "png")):
            template_json["message"]["photo"] = extract_photo_info(uploaded_file)

        elif file_name.endswith(("docx", "pdf", "xslx", ".pptx")):
            template_json["message"]["document"] = extract_document_info(uploaded_file)

        template_json["message"]["caption"] = data["message"]

    template_json["message"]["text"] = data["message"]

    update = telebot.types.Update.de_json(template_json)
    bot.process_new_updates([update])

    return jsonify({message: "ok"})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
