from . import suggestions
from flask import render_template, request
from ..models import Suggestion, db, Response
from flask import current_app, redirect, url_for
from app import bot


@suggestions.route("/")
def index():
    suggestions = db.query(Suggestion).all()
    unread = db.query(Suggestion).filter_by(is_read=False).count()
    current_app.logger.info(unread)
    return render_template(
        "./suggestions/index.html",
        include_js=False,
        suggestions=suggestions,
        unread=unread,
    )


@suggestions.route("/reply")
def reply_dormant():
    return render_template("./suggestions/reply.html", allowed=False)


@suggestions.route("<suggestion_id>/reply", methods=["POST", "GET"])
def reply(suggestion_id: str):
    if request.method == "POST":
        # ? I am considering keeping the message id so that reply_to can be used
        data = request.form
        current_app.logger.info(data)
        new_reply = Response(text=data["message"], suggestion_id=suggestion_id)
        db.add(new_reply)
        db.commit()

        bot.send_message(
            db.query(Suggestion).get(suggestion_id).sender.chat_id, data["message"]
        )
        return render_template("./messages/success.html", allowed=True)

    # ? Wheter or not we should store replies as a database entity is something i'm still thinking about but yes for now
    suggestion = db.query(Suggestion).get(suggestion_id)
    return render_template(
        "./suggestions/reply.html", suggestion=suggestion, allowed=True
    )


@suggestions.route("<suggestion_id>/read")
def read_suggestion(suggestion_id: str):
    suggestion = db.query(Suggestion).get(suggestion_id)
    suggestion.is_read = True
    db.commit()
    return redirect(url_for("suggestions.index"))
