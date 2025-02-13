from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Uuid,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

url = os.getenv("SQLALCHEMY_DATABASE_URI")


# Create an engine
engine = create_engine(url, echo=True)

# Create a base class
Base = declarative_base()


# Define a simple model
class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True)
    chat_id = Column(Integer)
    college = Column(String)
    level = Column(String)

    suggestions = relationship("Suggestion", back_populates="sender")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    text = Column(Text)
    filename = Column(String)


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Uuid, primary_key=True)
    text = Column(Text)
    date = Column(DateTime, default=datetime.now)
    
    sender_id = Column(Uuid, ForeignKey('users.id'))
    replies = relationship("Response", back_populates="suggestion")

class Response(Base):
    __tablename__ = "responses"

    id = Column(Uuid, primary_key=True)
    text = Column(Text)
    date = Column(DateTime, default=datetime.now)
    
    suggestion_id = Column(Uuid, ForeignKey('suggestions.id'))

# Create all tables
Base.metadata.create_all(engine)

# Create a configured "Session" class
session = sessionmaker(bind=engine)
