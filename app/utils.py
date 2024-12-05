from werkzeug.datastructures import FileStorage
import os
from PIL import Image
from telebot.types import InputFile


def extract_photo_info(file: FileStorage):
    # Save the file locally
    file_path = os.path.join(r"app\files", file.filename)
    file.save(file_path)

    with Image.open(file_path) as img:
        width, height = img.size

    return InputFile(file_path), width, height


def extract_document_info(file: FileStorage):
    # Save the file locally
    file_path = os.path.join(r"app\files", file.filename)
    file.save(file_path)

    return InputFile(file_path)
