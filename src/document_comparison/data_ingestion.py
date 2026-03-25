import sys
import os
from pathlib import Path
import fitz

from logger.custom_logger import logger as log
from exception.custom_exception import DocumentQueryingPortalException

class DataIngestionForDocumentComparison:
    def __init__(self, base_directory):
        log.info("Initializing DataIngestionForDocumentComparison...")

        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)
        log.info(f"Base directory set to: {self.base_directory}")

    def delete_existing_files(self):
        """Delete existing files in the specfied directory."""
        try:
            pass
        except Exception as e:
            log.error(f"Error deleting existing files: {e}")
            raise DocumentQueryingPortalException("Failed to delete existing files", sys)

    def save_uploaded_files(self):
        """Save uploaded files to the specified directory."""
        try:
            pass
        except Exception as e:
            log.error(f"Error saving uploaded files: {e}")
            raise DocumentQueryingPortalException("Failed to save uploaded files", sys)

    def read_pdf(self, pdf_path):
        """Read the contents of a PDF file."""
        try:
            with fitz.open(self, pdf_path) as doc:
                if doc.is_encrypted:
                    log.warning(f"PDF file is encrypted: {pdf_path}")
                    raise ValueError("PDF file is encrypted", pdf_path)
                
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                
                    if text.strip():
                        log.info(f"Extracted text from page {page_num + 1} of {pdf_path}")
                        all_text.append(f"____Page {page_num + 1}____\n{text}\n")
                
                log.info(f"Successfully read PDF file: {pdf_path}")
                return "\n".join(all_text)

        except Exception as e:
            log.error(f"Error reading PDF file: {e}")
            raise DocumentQueryingPortalException("Failed to read PDF file", sys)
