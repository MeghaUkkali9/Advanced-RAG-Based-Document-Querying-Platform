import os
import sys
import fitz 
import uuid
from datetime import datetime
from pathlib import Path

from logger.logger_instance import logger as log
from exception.custom_exception import DocumentQueryingPortalException


class DataIngestion:
    """
    Handles PDF saving, reading, and text extraction.
    """

    def __init__(self, data_dir=None, session_id=None):
        try:
            base_dir = Path(__file__).resolve().parent

            data_dir = data_dir or os.getenv(
                "DATA_STORAGE_DIR",
                os.path.join(os.getcwd(), "data", "document_analysis")
            )

            self.session_id = session_id or (
                f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                f"{uuid.uuid4().hex[:8]}"
            )

            self.session_path = os.path.join(data_dir, self.session_id)
            os.makedirs(self.session_path, exist_ok=True)

            log.info(
                "DataIngestion initialized",
                session_id=self.session_id,
                session_path=self.session_path
            )

        except Exception as e:
            log.error(f"Error initializing DataIngestion: {e}")
            raise DocumentQueryingPortalException(e, sys)

    def save_pdf(self, uploaded_file):
        try:
            filename = os.path.basename(uploaded_file.name)

            if not filename.lower().endswith(".pdf"):
                raise DocumentQueryingPortalException(
                    "Invalid file type. Only PDFs are allowed.",
                    sys
                )
            
            save_path = os.path.join(self.session_path, filename)

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            log.info("PDF saved successfully", file=filename, file_path=save_path, session_id=self.session_id)
            return save_path

        except Exception as e:
            log.error(f"Error saving PDF: {e}")
            raise DocumentQueryingPortalException(e, sys)
        
    def read_pdf(self, pdf_path):
        try:
            text_chunks = []
            with fitz.open(pdf_path) as doc:
                for page_num, page in enumerate(doc, start=1):
                    text_chunks.append(f"--- Page {page_num} ---\n{page.get_text()}\n")
            text = "\n".join(text_chunks)
            log.info("PDF read and text extracted successfully", session_id=self.session_id, pdf_path=pdf_path)
            return text
        except Exception as e:
            log.error(f"Error loading PDF: {e}")
            raise DocumentQueryingPortalException(e, sys)

if __name__ == "__main__":
    from pathlib import Path
    from io import BytesIO
    file_path = r"/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_analysis/Attention_is_all_you_need.pdf"

    class UploadedFile:
        def __init__(self, path):
            self.name = Path(path).name
            self._file_path = path

        def getbuffer(self):
            return open(self._file_path, "rb").read()

    uploaded_file = UploadedFile(file_path)

    ingestion = DataIngestion(session_id="test_session")
    try:
        saved_path = ingestion.save_pdf(uploaded_file)
        print(f"PDF saved at: {saved_path}")

        read_text = ingestion.read_pdf(saved_path)
        print(f"Extracted text length: {len(read_text)} characters")
        
    except Exception as e:
        log.error(f"Test failed: {e}")
        raise DocumentQueryingPortalException("Test failed", sys)