from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from dotenv import load_dotenv
import os

load_dotenv()


Base = declarative_base()

Engine = create_engine(
    os.getenv("DATABASE_URL"), echo=bool(os.getenv("SQLALCHEMY_ECHO"))
)

Session = sessionmaker(bind = Engine)
session = Session()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, unique=True)
    college = Column(String)
    level = Column(Integer)

    def __repr__(self):
        return f"<User {self.chat_id}>"