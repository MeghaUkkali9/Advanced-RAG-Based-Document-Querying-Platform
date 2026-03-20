import os
import fitz
import uuid
from datetime import datetime

from logger.logger_instance import logger as log
from exception.custom_exception import DocumentQueryingPortalException

class DataIngestion:
    """
    Handles PDF saving and reading operations.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.document = None
    
    def save_pdf(self, content: bytes):
        pass

    def load_pdf(self):
        try:
            with open(self.file_path, "rb") as f:
                self.document = fitz.open(f)
            log.info(f"PDF loaded successfully: {self.file_path}")
        except Exception as e:
            log.error(f"Error loading PDF: {e}")
            raise DocumentQueryingPortalException("Failed to load PDF")

    def extract_text(self):
        if not self.document:
            log.warning("Document not loaded")
            return ""

        text = ""
        for page in self.document:
            text += page.get_text()
        log.info("Text extracted successfully")
        return text

    def close_document(self):
        if self.document:
            self.document.close()
            log.info("Document closed successfully")