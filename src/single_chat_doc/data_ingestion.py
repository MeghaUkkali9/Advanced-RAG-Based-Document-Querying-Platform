import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException
from utils.model_loader import ModelLoader
from datetime import datetime

class SingleDocIngestor:
    def __init__(self, data_dir:str = "data/single_doc_chat", faiss_dir: str = "faiss_index"):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()
            self.log.info("SingleDocIngestor Initialized", temp_path=str(self.data_dir), faiss_dir=str(self.faiss_dir))
        except Exception as e:
            self.log("Failed to intialize singleDoc Ingestor", error=str(e))
            raise DocumentQueryingPortalException("Initialization error in SingleDocIngestor", sys)

    def ingest_document(self, uploaded_files):
        try:
            documents = []

            for uploaded_file in uploaded_files:
                unique_filename = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                temp_path = self.data_dir / unique_filename

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())
                
                self.log.info("PDF saved for ingestion", file_name= uploaded_file.name)
                loader = PyPDFLoader(str(temp_path))
                docs = loader.load()
                documents.extend(docs)
            self.log.info("PDF files loaded", count=len(documents))

            return self._create_retriever(documents)
        except Exception as e:
            self.log.error(f"Error ingesting document: {e}")
            raise DocumentQueryingPortalException("Failed to ingest document", sys)
        
    def _create_retriever(self, documents):
        try:
            spiltter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 300
            )
            chunks= spiltter.split_documents(documents)
            self.log.info("Documents split into chunks")

            embedding = self.model_loader.load_embeddings()

            vector_store = FAISS.from_documents(chunks, embedding)

            vector_store.save_local(str(self.faiss_dir))
            self.log.info("FAISS index created and saved", faiss_path= str(self.faiss_dir))

            retriver = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            self.log.info("Retriver created succesfully", retriver_type=str(retriver))

            return retriver
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentQueryingPortalException("Failed to create retriever", sys)
