from dotenv import load_dotenv
import os


load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    def init_app(app):
        pass


class DevelopmentConfig(Config):
    pass



config_dict = {
    "development": DevelopmentConfig
}
