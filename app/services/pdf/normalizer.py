import re


class TextNormalizer:

    @staticmethod
    def normalize(text: str) -> str:
        """
        Remove espaços e quebras de linha desnecessárias.
        """

        text = text.replace("\r", "")

        # Remove múltiplas quebras de linha
        text = re.sub(r"\n+", "\n", text)

        # Remove múltiplos espaços
        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()