from flask import Flask, render_template
from config import config_dict
import logging
import telebot
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
bot = telebot.TeleBot(os.getenv("BOT_API_KEY"))

webhook_url = os.getenv("WEBHOOK_URL")
bot.remove_webhook()
bot.set_webhook(webhook_url)


def format_datetime(value: datetime, format="%a, %d %b %Y ; %r"):
    return value.strftime(format)


def server_error():
    return render_template(
        "messages/failure.html",
        reason="There seems to be an error on our end please contact us to fix it",
    )


def create_app(config="development"):
    app = Flask(__name__)
    app.config.from_object(config_dict[config])

    app.jinja_env.filters["datetime"] = format_datetime

    config_dict[config].init_app(app)

    from .suggestions import suggestions

    app.register_blueprint(suggestions, url_prefix="/suggestions")

    from .announcements import announcements

    app.register_blueprint(announcements, url_prefix="/announcements")

    app.logger.level = logging.DEBUG
    app.logger.info(bot.get_webhook_info())

    app.register_error_handler(500, server_error)

    app.logger.info(app.url_map)

    return app
