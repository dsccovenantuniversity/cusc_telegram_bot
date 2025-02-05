from telebot import TeleBot
from colorama import init, Fore, Style
from app.models import create_user, get_user_info, update_user_profile
from werkzeug.datastructures import FileStorage

import logging
from dotenv import load_dotenv

load_dotenv()


init(autoreset=True)


class ParseError(Exception):
    pass


def setup_user(bot: TeleBot, chat_id: int, message: str):
    """
    * sets up a user in the database
    """
    current_user = get_user_info(chat_id)

    if not current_user:
        if message == "/start":
            create_user(chat_id)
            bot.send_message(
                chat_id,
                "Welcome to the CUSC announcement bot, please enter your college and level to verify your studentship like this: \n \n CMSS 200",
            )
            logging.info(f"New user created, chat_id = {chat_id}")
            return
        else:
            bot.send_message(
                chat_id, "Please run the /start command to record yourself"
            )
            return
    else:
        try:
            user_info = parse_message(message)

            if current_user["college"] or current_user["level"]:
                bot.send_message(chat_id, "You have already been verified")
                return
            else:
                update_user_profile(chat_id, user_info[1], user_info[0])
                bot.send_message(chat_id, "You have been successfully verified")
                return

        except ParseError as error:
            bot.send_message(chat_id, str(error))
            logging.error(error)
            return


def parse_message(message: str):
    """
    * parses this kind of message: CMSS 200 into ["CMSS", "200"] and validates it
    """
    if " " not in message:
        raise ParseError("Invalid message format")
    values = message.split(" ")

    if len(values) != 2:
        raise ParseError("Invalid message format")
    college = values[0]
    level = values[1]
    if college not in ["CMSS", "COE", "CST", "CLDS"]:
        raise ParseError("Invalid College")

    if level not in ["100", "200", "300", "400"]:
        if college in ["COE", "CST"] and level == "500":
            return college, level
        raise ParseError("Invalid Level")
    return college, level


def mass_send_document(users, bot: TeleBot, file, filename, caption):
    # * Send to first user
    message = bot.send_document(
        users[0]["chat_id"], file, visible_file_name=filename, caption=caption
    )

    file_id = message.document.file_id

    # * Use file id to send to the rest
    for user in users[1:]:
        bot.send_document(
            user["chat_id"], file_id, visible_file_name=filename, caption=caption
        )


def mass_send_photos(users, bot: TeleBot, photos, photo_name):
    # * Send to first user
    message = bot.send_photo(users[0]["chat_id"], photos, caption=photos.filename)

    file_id = message.photo[-1].file_id

    # * Use file id to send to the rest
    for user in users[1:]:
        bot.send_photo(user["chat_id"], file_id, caption=photos.filename)


class CustomFormatter(logging.Formatter):
    """Custom logging formatter to add colors to log messages."""

    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"{Fore.BLUE}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.INFO:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Fore.MAGENTA}{record.msg}{Style.RESET_ALL}"
        return super().format(record)
