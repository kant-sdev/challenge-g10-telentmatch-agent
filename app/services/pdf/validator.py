from fastapi import UploadFile

from app.core.exceptions import PDFProcessingException


ALLOWED_TYPES = [
    "application/pdf"
]


def validate_pdf(file: UploadFile):

    if file.content_type not in ALLOWED_TYPES:
        raise PDFProcessingException(
            "Arquivo enviado não é um PDF válido"
        )

    return True