import sys
import os
import uuid

from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from exception.custom_exception import DocumentQueryingPortalException
from logger.custom_logger import CustomLogger
from utils.model_loader import ModelLoader

class DocumentIngestor:
    SUPPORTED_FILE_TYPES = {'.pdf', '.docx', '.txt', '.md'}

    def __init__(self, temp_dir:str="data/multi_doc_chat", faiss_dir:str="faiss_index", sesssion_id:str=None):
        self.log = CustomLogger().get_logger(__name__)
        try:
            
            #base dirs
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)

            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)

            self.sesssion_id = sesssion_id or f"session_id_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            self.session_temp_dir = self.temp_dir / self.sesssion_id
            self.session_temp_dir.mkdir(parents=True, exist_ok=True)

            self.session_faiss_dir = self.faiss_dir / self.sesssion_id
            self.session_faiss_dir.mkdir(parents=True, exist_ok=True)

            self.model_loader = ModelLoader()

            self.log.info("Initializing is completed")
        except Exception as e:
            self.log.error("Error in initializing DocumentIngestor")
            raise DocumentQueryingPortalException("Initialization error in DocumentIngestor", sys)

    def ingest_files(self, uploaded_files):
        try:
            documents = []

            for uploaded_file in uploaded_files:
                file_extension = Path(uploaded_file.name).suffix.lower()

                if file_extension not in self.SUPPORTED_FILE_TYPES:
                    self.log.warning("Unsupported file is skipped", file_name= uploaded_file)
                    continue

                unique_file_name = f"{uuid.uuid4().hex[:8]}{file_extension}"
                temp_path = self.session_temp_dir / unique_file_name

                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.read())

                self.log.info("filesaved sussfully", file_name=uploaded_file.name, saved_at=str(temp_path), session_id= self.sesssion_id)

                if file_extension == ".pdf":
                    loader = PyPDFLoader(str(temp_path))
                elif file_extension == ".docx":
                    loader = Docx2txtLoader(str(temp_path))
                elif file_extension == ".txt":
                    loader = TextLoader(str(temp_path), encoding="utf-8")
                else:
                    self.log.warning("Unsupported filetype encountered", file_name = uploaded_file.name)

                doc = loader.load()
                documents.extend(doc)

                if not documents:
                    raise DocumentQueryingPortalException("No Valid documents loaded", sys)
                
            self.log.info("All documents are loaded")
            return self.__create_retriever(documents=documents)
        except Exception as e:
            self.log.info("Error while ingesting files in DocumentIngestor", error = str(e))
            raise DocumentQueryingPortalException("Couldn't ingest the files")
        
    def __create_retriever(self, documents):
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 300
            )

            chunks = splitter.split_documents(documents)
            self.log.info("Documents split into chunks", total_chunks=len(chunks), session_id=self.sesssion_id)

            embeddings = self.model_loader.load_embeddings()

            vector_store = FAISS.from_documents(documents=chunks, embedding=embeddings)

            vector_store.save_local(str(self.session_faiss_dir))
            self.log.info("FAISS index created and saved", faiss_path= str(self.faiss_dir))

            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":5})
            self.log.info("Retriver created succesfully", retriver_type=str(retriever))

            return retriever
        except Exception as e:
            self.log.info("Error while creating retriver in DocumentIngestor", error = str(e))
            raise DocumentQueryingPortalException("Couldn't ingest the files")
        
        