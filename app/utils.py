from werkzeug.datastructures import FileStorage
import os
from PIL import Image
import json
from uuid import uuid1


def extract_photo_info(file: FileStorage):
    # Save the file locally
    file_path = os.path.join(r"app\files", file.filename)
    file.save(file_path)

    with Image.open(file_path) as img:
        width, height = img.size

    return [
        {
            "file_id": file_path,
            "file_unique_id": uuid1(),
            "width": width,
            "height": height,
        }
    ]


def extract_document_info(file: FileStorage):
    # Save the file locally
    file_path = os.path.join(r"app\files", file.filename)
    file.save(file_path)

    return {
        "file_id": file_path,
        "file_unique_id": uuid1(),
        "file_name": file.filename,
        "file_size": os.path.getsize(file_path),
    }
