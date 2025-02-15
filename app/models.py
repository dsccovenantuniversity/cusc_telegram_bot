from sqlalchemy import (
    create_engine,
    Column,
    String,
    Uuid,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
from uuid import uuid4

url = os.getenv("SQLALCHEMY_DATABASE_URI")


# Create an engine
engine = create_engine(url, echo=True)

# Create a base class
Base = declarative_base()


# Define a simple model
class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid4)
    chat_id = Column(String)
    college = Column(String)
    level = Column(String)

    suggestions = relationship("Suggestion", back_populates="sender")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid, primary_key=True, default=uuid4)
    date = Column(DateTime, default=datetime.now)
    text = Column(Text)
    filename = Column(String)
    college = Column(String)
    level = Column(String)


class Suggestion(Base):
    __tablename__ = "suggestions"

    id = Column(Uuid, primary_key=True, default=uuid4)
    text = Column(Text)
    date = Column(DateTime, default=datetime.now)
    is_read = Column(Boolean, default=False)

    sender_id = Column(Uuid, ForeignKey("users.id"))
    sender = relationship("User", back_populates="suggestions")
    replies = relationship("Response", back_populates="suggestion")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Uuid, primary_key=True, default=uuid4)
    text = Column(Text)
    date = Column(DateTime, default=datetime.now)

    suggestion_id = Column(Uuid, ForeignKey("suggestions.id"))
    suggestion = relationship("Suggestion", back_populates="replies")


# Create all tables
Base.metadata.create_all(engine)

# Create a configured "Session" class
_Session = sessionmaker(bind=engine)
db = _Session()
