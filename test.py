# import os
# from pathlib import Path

# from src.doc_analyzer.data_ingestion import DataIngestion
# from src.doc_analyzer.data_analysis import DataAnalyzer

# PDF_PATH = r"/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_analysis/Transformer.pdf"

# class TestDocumentProcessing:
#     def __init__(self, file_path=PDF_PATH):
#         self.file_path = file_path
#         self.name = Path(file_path).name

#     def getbuffer(self):
#         return open(self.file_path, "rb").read()
    
# def main():
#     try:
#         print("Starting test for document processing...")
#         uploaded_file = TestDocumentProcessing()
#         handler = DataIngestion(session_id="test_Ingestion_analysis")
#         saved_path = handler.save_pdf(uploaded_file)
#         print(f"PDF saved at: {saved_path}")

#         read_text = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(read_text)} characters")
#         print(f"Extracted text preview:\n{read_text[:500]}...")

#         analyzer = DataAnalyzer()
#         analysis_result = analyzer.analyze_document(read_text)
#         print(f"Document analysis result: {analysis_result}")

#         print("Test completed successfully.")
#         print("\n ==========Metadata Extracted==========")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test failed: {e}")
#         raise Exception("Test failed") from e

# if __name__ == "__main__":
#     main()


import io
from pathlib import Path

from src.document_comparison.data_ingestion import DataIngestionForDocumentComparison   
from src.document_comparison.document_comparison import DocumentComparator

def load_test_files(file_path: Path):
    return io.BytesIO(file_path.read_bytes())

def test_compare_documents():
   
    reference_file = Path("/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_compare/reference.pdf")
    actual_file = Path("/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_compare/actual.pdf")
    
    class TestFile:
        def __init__(self, file_path):
            self.name = file_path.name
            self._buffer = file_path.read_bytes()
            
        def getbuffer(self):
            return self._buffer
        
    ref_upload = TestFile(reference_file)
    actual_upload = TestFile(actual_file)

    comparator = DataIngestionForDocumentComparison()

    ref_file, actual_file = comparator.save_uploaded_files(ref_upload, actual_upload)
    combined_docs = comparator.combine_documents()

    print("Combined document content preview:")
    print(combined_docs[:1000])  # Print the first 1000 characters of

    llm_comparator = DocumentComparator()
    comparison_result = llm_comparator.compare_documents(combined_docs)
    print("Comparison result:")
    print(comparison_result.head())  # Print the first few rows of the comparison result

if __name__ == "__main__":
        test_compare_documents()
