import sys
import os
from pathlib import Path
import fitz
import shutil
from datetime import datetime
import uuid

from exception.custom_exception import DocumentQueryingPortalException
from logger.custom_logger import CustomLogger

log = CustomLogger().get_logger(__name__)

log.info("This works perfectly")
class DataIngestionForDocumentComparison:
    def __init__(self, base_directory:str="data/document_compare", session_id:str=None):
        log.info("Initializing DataIngestionForDocumentComparison...")

        self.base_directory = Path(base_directory)
        self.base_directory.mkdir(parents=True, exist_ok=True)
        log.info(f"Base directory set to: {self.base_directory}")

        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path = self.base_directory / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
        log.info(f"Session initialized with ID: {self.session_id} at path: {self.session_path}")

    def delete_existing_files(self):
        """Delete existing files in the specfied directory."""
        try:
            if self.base_directory.exists() and self.base_directory.is_dir():
                for file in self.base_directory.iterdir():
                    if file.is_file():
                        file.unlink()
                        log.info(f"Deleted existing file: {file}")
            else:
                log.warning(f"Base directory does not exist or is not a directory: {self.base_directory}")
        except Exception as e:
            log.error(f"Error deleting existing files: {e}")
            raise DocumentQueryingPortalException("Failed to delete existing files", sys)

    def save_uploaded_files(self, reference_file, actual_file):
        """Save uploaded files to the specified directory."""
        try:
            self.delete_existing_files()
            log.info("Saving uploaded files...")

            reference_path=self.session_path / reference_file.name
            actual_path=self.session_path / actual_file.name

            if not reference_file.name.endswith('.pdf') or not actual_file.name.endswith('.pdf'):
                log.warning("One or both uploaded files are not PDFs")
                raise ValueError("Both uploaded files must be PDFs")
            
            with open(reference_path, 'wb') as ref_file:
                ref_file.write(reference_file.getbuffer())
            log.info(f"Reference file saved successfully: {reference_path}")

            with open(actual_path, 'wb') as act_file:
                act_file.write(actual_file.getbuffer())
            log.info(f"Actual file saved successfully: {actual_path}")

            return reference_path, actual_path
        except Exception as e:
            log.error(f"Error saving uploaded files: {e}")
            raise DocumentQueryingPortalException("Failed to save uploaded files", sys) 
        
    def read_pdf(self, pdf_path):
        """Read the contents of a PDF file."""
        try:
            with fitz.open(pdf_path) as doc:
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
        
    def combine_documents(self):
        """Combine the contents of the reference and actual documents."""
        try:
            content_dict = {}
            doc_parts = []

            for filename in sorted(self.base_directory.iterdir()):
                if filename.is_file() and filename.suffix == '.pdf':
                    content_dict[filename.name] = self.read_pdf(filename)
            
            for filename, content in content_dict.items():
                doc_parts.append(f"Document: {filename}-{content}\n")
            
            combined_content = "\n".join(doc_parts)
            log.info("Documents combined successfully")
            return combined_content
        except Exception as e:
            log.error(f"Error combining documents: {e}")
            raise DocumentQueryingPortalException("Failed to combine documents", sys)
        
    def clean_old_sessions(self, keep_latest: int = 3):
        try:
            sessions = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()], 
                reverse=True)
            
            for folder in sessions[keep_latest:]:
                shutil.rmtree(folder, ignore_errors=True)
                log.info("Old session folder deleted", path=str(folder))
        except Exception as e:
            log.error("Error cleaning old sessions", error=str(e))
            raise DocumentQueryingPortalException("Error cleaning old sessions", e) from e
