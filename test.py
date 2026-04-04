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


# import io
# from pathlib import Path

# from src.document_comparison.data_ingestion import DataIngestionForDocumentComparison   
# from src.document_comparison.document_comparison import DocumentComparator

# def load_test_files(file_path: Path):
#     return io.BytesIO(file_path.read_bytes())

# def test_compare_documents():
   
#     reference_file = Path("/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_compare/reference.pdf")
#     actual_file = Path("/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/document_compare/actual.pdf")
    
#     class TestFile:
#         def __init__(self, file_path):
#             self.name = file_path.name
#             self._buffer = file_path.read_bytes()
            
#         def getbuffer(self):
#             return self._buffer
        
#     ref_upload = TestFile(reference_file)
#     actual_upload = TestFile(actual_file)

#     comparator = DataIngestionForDocumentComparison()

#     ref_file, actual_file = comparator.save_uploaded_files(ref_upload, actual_upload)
#     combined_docs = comparator.combine_documents()
#     comparator.clean_old_sessions()
    
#     print("Combined document content preview:")
#     print(combined_docs[:1000]) 

#     llm_comparator = DocumentComparator()
#     comparison_result = llm_comparator.compare_documents(combined_docs)
#     print("\nComparison result:")
#     print(comparison_result.to_dict(orient='records')) 
    
# if __name__ == "__main__":
#         test_compare_documents()


# Test for document chat
# import sys
# from pathlib import Path

# from langchain_community.vectorstores import FAISS
# from src.single_document_chat.data_ingestion import SingleDocIngestor
# from src.single_document_chat.retrieval import ConversationalRetrieval
# from utils.model_loader import ModelLoader

# FAISS_INDEX_PATH = Path("faiss_index")

# def test_convertaional_rag_on_pdf(pdf_path, question):
#     try:
#         model_loader = ModelLoader()
       
#         if FAISS_INDEX_PATH.exists():
#             print("Loading existing FAISS index")
#             embeddings = model_loader.load_embeddings()
#             vector_store = FAISS.load_local(folder_path=str(FAISS_INDEX_PATH), embeddings=embeddings, allow_dangerous_deserialization=True)
#             retriver = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":5})

#         else:
#             print("FAISS INDEX not found, ingest PDF and create index")
#             with open(pdf_path, 'rb') as f:
#                 uploaded_files = [f]
#                 ingestor = SingleDocIngestor()
#                 retriver = ingestor.ingest_document(uploaded_files=uploaded_files)
#         print("Running Conversational RAG,,,,,,")
#         session_id = "test_conversational_rag"
#         rag = ConversationalRetrieval(retriever=retriver, session_id=session_id)

#         response = rag.invoke(question)
#         print(f"\n Question:{question} \n Answer:{response}")

#     except Exception as e:
#         print(f"Test:failed: {str(e)}")
#         sys.exit(1)

# if __name__ == "__main__":
#     pdf_path = r"/Users/meghaukkali/Documents/Advanced-RAG-Based-Document-Querying-Platform/data/single_doc_chat/Transformer.pdf"
#     question = "What is the main topic of the document?"

#     if not Path(pdf_path).exists():
#         print(f"PDF file does not exist at: {pdf_path}")
#         sys.exit(1)

#     test_convertaional_rag_on_pdf(pdf_path=pdf_path, question=question)

#Testing for multidoc chat

import sys
from pathlib import Path
from src.multi_doc_chat.data_ingestion import DocumentIngestor
from src.multi_doc_chat.retrieval import ConversationalRAG

def test_document_ingetion_and_rag():
    try:
        test_files = [
            "data/multi_doc_chat/Generative-AI-pt-ai-Zant-Kouw-Schomaker.pdf",
            "data/multi_doc_chat/NaturalLanguageProcessing-paper-Al-Taani-2021.pdf",
            "data/multi_doc_chat/NLP for smart healthcare.pdf",
            "data/multi_doc_chat/Transformer.pdf"
        ]

        uploaded_files = []
        for file_path in test_files:
            if Path(file_path).exists():
                uploaded_files.append(open(file_path, "rb"))
            else:
                print(f"File not existed", {file_path})

        if not uploaded_files:
            print("No valid files to upload.")
            sys.exit(1)

        doc_ingestor = DocumentIngestor()
        ingested_retriever = doc_ingestor.ingest_files(uploaded_files)
        
        for f in uploaded_files:
            f.close()
            
        session_id = "test_multi_doc_chat"
        rag = ConversationalRAG(session_id=session_id, retriever=ingested_retriever)
        question = "what is all abount NLP for smart healthcare?"

        answer = rag.invoke(question)
        print("\n Question:", question)
        print("Answer", answer)
            
    except Exception as e:
        print(f"test failed: {str(e)}")
        sys.exit()

if __name__ == "__main__":
    test_document_ingetion_and_rag()