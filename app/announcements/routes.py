from flask import request, render_template, current_app
from dotenv import load_dotenv
from . import announcements
from ..utils.utils import setup_user, mass_send_message, mass_send_document
from ..models import Message, db
from sqlalchemy.exc import SQLAlchemyError


load_dotenv()


@announcements.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    current_app.logger.info(data)

    if data.get("message"):
        setup_user(data["message"]["text"], str(data["message"]["chat"]["id"]))

    return {"ok": True}


@announcements.route("/announce", methods=["POST", "GET"])
def announce():
    if request.method == "POST":
        data = request.form
        college = data["colleges"]
        level = data["levels"]
        new_message = Message(college=college.split(" ")[0], level=level.split(" ")[0])

        if not data["message"] and not request.files:
            return render_template(
                "messages/failure.html", reason="No message provided"
            )

        if request.files:
            new_message.filename = request.files["file"].filename
            mass_send_document(request.files["file"], college, level)

        if data["message"]:
            new_message.text = data["message"]
            mass_send_message(data["message"], college, level)

        current_app.logger.info(data)

        try:
            db.add(new_message)
            db.commit()
        except SQLAlchemyError as err:
            current_app.logger.error(err)
            db.rollback()

        return render_template("messages/success.html")
    return render_template("announcements/index.html", include_js=True)


@announcements.route("/messages", methods=["GET"])
def messages():
    all_messages = db.query(Message).all()
    return render_template("announcements/messages.html", all_messages=all_messages)
