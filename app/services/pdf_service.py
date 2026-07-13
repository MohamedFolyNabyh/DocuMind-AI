from pathlib import Path
import logging
import re

from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict

from app.config.settings import settings

logger = logging.getLogger(__name__)


class PDFService:

    def __init__(self):

        self.model_dict = create_model_dict()

        self.converter = PdfConverter(
            artifact_dict=self.model_dict
        )

        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "h1"),
                ("##", "h2"),
                ("###", "h3"),
                ("####", "h4"),
            ]
        )

        self.chunk_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def extract_markdown(self,pdf_path: Path) -> str:
        """
        Convert PDF to Markdown.
        """

        rendered = self.converter(pdf_path)

        return rendered.markdown

    def clean_markdown(self, markdown: str) -> str:
        """
        Clean markdown before chunking.
        """

        markdown = markdown.replace("\r\n", "\n")
        markdown = markdown.replace("\r", "\n")

        markdown = re.sub(r"(?im)^page\s+\d+\s*$","",markdown)

        markdown = re.sub(r"TABLE OF CONTENTS.*?(?=\n#|\Z)","", markdown,flags=re.IGNORECASE | re.DOTALL)

        markdown = re.sub( r"\n{3,}", "\n\n", markdown)

        markdown = re.sub(r"[ \t]{2,}"," ",markdown)

        markdown = markdown.replace("\u200b", "")
        markdown = markdown.replace("\u200c", "")
        markdown = markdown.replace("\xa0", " ")

        return markdown.strip()

    def split_headers(self,markdown: str) -> list[Document]:

        return self.header_splitter.split_text(
            markdown
        )

    def split_chunks(self,documents: list[Document]) -> list[Document]:

        return self.chunk_splitter.split_documents(
            documents
        )

    def process_pdf(self, pdf_path: Path) -> list[Document]:
        """
        Complete PDF pipeline.
        """

        logger.info("Processing PDF: %s",pdf_path.name)

        markdown = self.extract_markdown( pdf_path)

        markdown = self.clean_markdown(markdown)

        documents = self.split_headers( markdown)

        documents = self.split_chunks( documents)

        for index, document in enumerate(documents):

            document.metadata["chunk_id"] = index

            document.metadata["source"] = pdf_path.name

        logger.info("Generated %d chunks.",len(documents))

        return documents