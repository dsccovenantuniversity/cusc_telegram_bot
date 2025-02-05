from flask import Blueprint

announcements = Blueprint('announcements', __name__)

from . import routes