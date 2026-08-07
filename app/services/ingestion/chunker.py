from langchain_text_splitters import RecursiveCharacterTextSplitter


class Chunker:

    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def split(self, text: str) -> list[str]:
        return self.splitter.split_text(text)