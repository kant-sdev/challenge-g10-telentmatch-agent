from io import BytesIO

from pypdf import PdfReader

from app.core.exceptions import PDFProcessingException


def extract_text(file_bytes: bytes) -> str:

    try:

        pdf = PdfReader(
            BytesIO(file_bytes)
        )

        text = ""

        for page in pdf.pages:
            text += page.extract_text() or ""

        return text.strip()


    except Exception as e:

        raise PDFProcessingException(
            f"Erro ao ler PDF: {str(e)}"
        )