import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException
from utils.model_loader import ModelLoader

class SingleDocIngestor:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)


    def ingest_document(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error ingesting document: {e}")
            raise DocumentQueryingPortalException("Failed to ingest document", sys)
        
    def _create_retriever(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error creating retriever: {e}")
            raise DocumentQueryingPortalException("Failed to create retriever", sys)
