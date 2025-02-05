from flask import Blueprint

suggestions = Blueprint('suggestions', __name__)

from . import routes