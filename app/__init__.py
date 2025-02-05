from flask import Flask, render_template
from config import config_dict


def create_app(config="development"):

    app = Flask(__name__)
    app.config.from_object(config_dict[config])


    config_dict[config].init_app(app)

    from .suggestions import suggestions
    app.register_blueprint(suggestions, url_prefix="/suggestions")

    @app.errorhandler(500)
    def server_error():
        return render_template('messages/failure.html', reason = "There seems to be an error on our end please contact us to fix it")
    
    return app
