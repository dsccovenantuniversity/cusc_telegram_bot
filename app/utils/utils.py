from app import bot
from ..models import User, db, Suggestion
from sqlalchemy.exc import SQLAlchemyError
import logging
from werkzeug.datastructures import FileStorage
from typing import Literal


CollegeLiteral = Literal[
    "All Colleges", "CMSS Students", "CST Students", "COE Students", "CLDS Students"
]
LevelLiteral = Literal[
    "All Levels",
    "100 Level Students",
    "200 Level Students",
    "300 Level Students",
    "400 Level Students",
    "500 Level Students",
]


class ParseException(Exception):
    pass


def filter(_college: CollegeLiteral, _level: LevelLiteral):
    college = _college.split(" ")[0]
    level = _level.split(" ")[0]

    if college == "All":
        college = None

    if level == "All":
        level = None

    query = db.query(User)
    query = query.filter(User.college == college) if college else query
    query = query.filter(User.level == level) if level else query

    return query


def setup_user(message: str, chat_id: int):

    #! Oga yii, shorten this function jor
    if message.startswith("/suggest"):
        suggest_message = message[8:]

        if len(suggest_message) < 6:
            # XXX whitespaces are also considered characters.
            bot.send_message(chat_id, "The message is too short")
            return

        user = db.query(User).filter_by(chat_id=chat_id).first()

        if not user:
            bot.send_message(chat_id, "You are not registered")
            return
        
        suggestion = Suggestion(sender=user, text=message[8:])
        try:
            db.add(suggestion)
            db.commit()
            bot.send_message(chat_id, "Suggestion sent successfully")
        except SQLAlchemyError as error:
            logging.error(error)
            db.rollback()
            bot.send_message(chat_id, "An error occurred while sending the suggestion")
        return

    if message == "/start":
        if not db.query(User).filter_by(chat_id=chat_id).first():
            user = User(chat_id=chat_id)
            try:
                db.add(user)
                db.commit()
            except SQLAlchemyError as error:
                logging.error(error)
            bot.send_message(
                chat_id,
                "Hey there! Welcome to the CUSC Announcement Bot. 🎉\n\n"
                "Got a suggestion for the student council? Just type */suggest your message*.\n\n"
                "To get started and register, please enter your college and level like this:\n"
                "*CST 400*\n"
                "Looking forward to having you on board! 😊", "Markdown"
            )
        else:
            bot.send_message(chat_id, "You are already registered")
    else:
        if not db.query(User).filter_by(chat_id=chat_id).first():
            bot.send_message(chat_id, "You are not registered")

        else:
            user = db.query(User).filter_by(chat_id=chat_id).first()

            if user.college and user.level:
                bot.send_message(
                    chat_id, "Your college and level has already been recorded"
                )
            else:
                try:
                    parse_message(message)
                    college, level = message.split(" ")

                    try:
                        user.college = college
                        user.level = level
                        db.commit()
                    except SQLAlchemyError as error:
                        logging.error(error)
                        db.rollback()

                    bot.send_message(chat_id, "You have been registered successfully")
                except ParseException as e:
                    bot.send_message(chat_id, str(e))


def parse_message(message: str):
    data = message.split(" ")
    if len(data) != 2:
        raise ParseException("Invalid message format")
    if data[0] not in ["CST", "CMSS", "COE", "CLDS"]:
        raise ParseException("Invalid college choose from CST, CMSS, COE, CLDS")
    if data[1] not in ["100", "200", "300", "400", "500"]:
        raise ParseException("Invalid level choose from 100, 200, 300, 400")

    if data[0] in ["CMSS", "CLDS"] and data[1] == "500":
        raise ParseException("Who are you whining? 😅")


def mass_send_message(message: str, college: CollegeLiteral, level: LevelLiteral):
    all_users = filter(college, level).all()
    for user in all_users:
        bot.send_message(user.chat_id, message)


def mass_send_document(
    document: FileStorage,
    college: CollegeLiteral,
    level: LevelLiteral,
    message: str | None = None,
):
    all_users = filter(college, level).all()

    sent = bot.send_document(
        all_users[0].chat_id,
        document.stream,
        caption=message,
        visible_file_name=document.filename,
    )

    for user in all_users[1:]:
        bot.send_document(
            user.chat_id,
            sent.document.file_id,
            caption=message,
            visible_file_name=sent.document.file_name,
        )
