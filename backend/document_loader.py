import os
from typing import List
import PyPDF2
import docx
from utils.logger import app_logger

class DocumentLoader:
    @staticmethod
    def load_pdf(file_path: str) -> str:
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            app_logger.error(f"Error loading PDF {file_path}: {e}")
        return text

    @staticmethod
    def load_docx(file_path: str) -> str:
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            app_logger.error(f"Error loading DOCX {file_path}: {e}")
        return text

    @staticmethod
    def load_txt(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            app_logger.error(f"Error loading TXT {file_path}: {e}")
            return ""

    @staticmethod
    def load_md(file_path: str) -> str:
        return DocumentLoader.load_txt(file_path)

    @classmethod
    def load_document(cls, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return cls.load_pdf(file_path)
        elif ext == ".docx":
            return cls.load_docx(file_path)
        elif ext == ".txt":
            return cls.load_txt(file_path)
        elif ext == ".md":
            return cls.load_md(file_path)
        else:
            app_logger.warning(f"Unsupported file extension: {ext}")
            return ""
