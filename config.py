from dotenv import load_dotenv


load_dotenv()

class Config:

    def init_app(app):
        pass


class DevelopmentConfig(Config):
    pass



config_dict = {
    "development": DevelopmentConfig
}
