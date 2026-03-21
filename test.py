import os
from pathlib import Path

from src.doc_analyzer.data_ingestion import DataIngestion
from src.doc_analyzer.data_analysis import DataAnalyzer

PDF_PATH = r"/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_analysis/Transformer.pdf"

class TestDocumentProcessing:
    def __init__(self, file_path=PDF_PATH):
        self.file_path = file_path
        self.name = Path(file_path).name

    def getbuffer(self):
        return open(self.file_path, "rb").read()
    
def main():
    try:
        print("Starting test for document processing...")
        uploaded_file = TestDocumentProcessing()
        handler = DataIngestion(session_id="test_Ingestion_analysis")
        saved_path = handler.save_pdf(uploaded_file)
        print(f"PDF saved at: {saved_path}")

        read_text = handler.read_pdf(saved_path)
        print(f"Extracted text length: {len(read_text)} characters")
        print(f"Extracted text preview:\n{read_text[:500]}...")


    except Exception as e:
        print(f"Test failed: {e}")
        raise Exception("Test failed") from e

