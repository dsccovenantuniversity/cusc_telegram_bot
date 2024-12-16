from werkzeug.datastructures import FileStorage
import os
from PIL import Image
from telebot.types import InputFile
from colorama import init, Fore, Style
import logging
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import requests

load_dotenv()


init(autoreset=True)


class ParseError(Exception):
    pass


def extract_photo_info(file: FileStorage):
    # Save the file locally
    file_path = os.path.join(r"app\files", file.filename)
    if not os.path.exists(file_path):
        file.save(file_path)

    with Image.open(file_path) as img:
        width, height = img.size

    return InputFile(file_path), width, height


def extract_document_info(file: FileStorage):
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    )


    # * Upload file to cloudinary
    upload_result = cloudinary.uploader.upload(file, public_id = file.filename, unique_filename = False, resource_type = "raw")
    upload_url = upload_result["secure_url"]

    logging.info(upload_url)

    # * Use requests to download file from url
    return upload_url


def parse_message(message: str):
    """
    * parses this kind of message: CMSS 200 into ["CMSS", "200"] and validates it
    """
    if " " not in message:
        raise ParseError("Invalid message format")
    values = message.split(" ")
    college = values[0]
    level = values[1]
    if college not in ["CMSS", "COE", "CST", "CLDS"]:
        raise ParseError("Invalid College")

    if level not in ["100", "200", "300", "400"]:
        if college in ["COE", "CST"] and level == "500":
            return college, level
        raise ParseError("Invalid Level")
    return college, level


class CustomFormatter(logging.Formatter):
    """Custom logging formatter to add colors to log messages."""

    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.msg = f"{Fore.BLUE}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.INFO:
            record.msg = f"{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            record.msg = f"{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.CRITICAL:
            record.msg = f"{Fore.MAGENTA}{record.msg}{Style.RESET_ALL}"
        return super().format(record)
