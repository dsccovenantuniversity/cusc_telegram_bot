from flask import Flask
from config import config_dict


def create_app(config="development"):

    app = Flask(__name__)
    app.config.from_object(config_dict[config])


    config_dict[config].init_app(app)

    from .routes import routes_blueprint
    app.register_blueprint(routes_blueprint, url_prefix="/")

    from . import routes
    from . import models

    return app
