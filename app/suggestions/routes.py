from . import suggestions
from flask import render_template


@suggestions.route("/")
def index():
    return render_template("./suggestions/index.html", include_js=False)


@suggestions.route("/reply")
def reply():
    return render_template("./suggestions/reply.html")


@suggestions.route("/announce")
def announce():
    return render_template("./announcements/index.html")


@suggestions.route("/messages")
def messages():
    return render_template("./announcements/messages.html")
