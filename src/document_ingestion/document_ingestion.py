import os
import sys
import json
import uuid
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Dict, Any
from __future__ import annotations

import fitz
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstore import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException

from utils.file_io import generate_session_id, save_uploaded_files
from utils.document_operations import load_documents, concat_for_analysis, concat_for_comparison

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
class FaissManager:
    def __init__(self, index_dir: Path, model_loader: Optional[ModelLoader]=None):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.meta_path = self.index_dir / "ingested_meta.json"
        self._meta: Dict[str, Any] = {"rows":{}}
        
        if self.meta_path.exists():
            try:
                self._meta = json.loads(self.meta_path.read_text(encoding="utf-8")) or {"rows": {}}
            except Exception as e:
                self._meta = {"rows": {}}
                
        self.model_loader = model_loader or ModelLoader()
        self.embeddings = self.model_loader.load_embeddings()
        self.vector_store: Optional[FAISS] = None

    def load_or_create(self,texts: Optional[List[str]]=None, metadatas: Optional[List[dict]] = None):
        if self.__exists():
            self.vector_store = FAISS.load_local(
                str(self.index_dir),
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True,
            )
            return self.vector_store
        
        if not texts:
            raise DocumentQueryingPortalException("No existing FAISS index and no data to create one", sys)
        
        self.vector_store = FAISS.from_texts(texts=texts, embedding=self.embeddings, metadatas=metadatas or [])
        self.vector_store.save_local(str(self.index_dir))
        
        return self.vector_store
    
    def add_documents(self, docs: List[Document]):
        if self.vector_store is None:
            raise RuntimeError("Call load_or_create before add_document_idempotent()")
        
        new_docs: List[Document] = []
        
        for doc in docs:
            key = self.__finger_print(doc.page_content, doc.metadata or {})
            if key in self._meta["rows"]:
                continue
            self._meta["rows"][key] = True
            new_docs.append(doc)
            
        if new_docs:
            self.vector_store.add_documents(new_docs)
            self.vector_store.save_local(str(self.index_dir))
            self.__save_metadata()
            
        return len(new_docs)
    
    def __exists(self) -> bool:
        return (self.index_dir / "index.faiss").exists() and (self.index_dir / "index.pkl").exists()
    
    @staticmethod
    #deduplication: remove duplicates from database
    def __finger_print(text: str, md:Dict[str, Any]) -> str:
        src = md.get("source") or md.get("file_path")
        rid = md.get("row_id")
        
        if src is not None:
            return f"{src}::{'' if rid is None else rid}"
        
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    def __save_metadata(self):
        self.meta_path.write_text(json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")

class DocumentHandler:
    """
    Save and read PDF for analysis
    """
    def __init__(self, data_dir: Optional[str] = None, session_id: Optional[str] = None):
        self.data_dir = data_dir or os.getenv(
                            "DATA_STORAGE_PATH", 
                            os.path.join(os.getcwd(), "data", "document_analysis")
                            )
        self.session_id = session_id or generate_session_id("session")
        
        self.session_path = os.path.join(self.data_dir, self.session_id)
        os.makedirs(self.session_path, exist_ok=True)
        
    def save_pdf(self, uploaded_file) -> str:
        try:
            filename = os.path.basename(uploaded_file.name)
            if not filename.lower().endswith(".pdf"):
                raise ValueError("Invalid file type. Only PDFs are allowed.")
            
            save_path = os.path.join(self.session_path, filename)
            
            with open(save_path, "wb") as file:
                if hasattr(uploaded_file, "read"):
                    file.write(uploaded_file.read())
                else:
                    file.write(uploaded_file.getbuffer())
            
            return save_path
        except Exception as e:
            raise DocumentQueryingPortalException(f"Failed to save PDF: {str(e)}", e)

    def read_pdf(self, pdf_path: str) -> str:
        try:
            text_chunks = []
            
            with fitz.open(pdf_path) as doc:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text_chunks.append(f"\n--- Page {page_num + 1} ---\n{page.get_text()}")
                    
            text = "\n".join(text_chunks)
            
            return text
        except Exception as e:
            raise DocumentQueryingPortalException(f"Could not process PDF: {pdf_path}", e)
    
class DocumentComparator:
    """
    Save, read & combine PDFs for comparison with session based versioning.
    """
    def __init__(self, base_dir: str = "data/document_compare", session_id: Optional[str] = None):
        self.base_dir = Path(base_dir)
        self.session_id = session_id or generate_session_id()
        
        self.session_path = self.base_dir / self.session_id
        self.session_path.mkdir(parents=True, exist_ok=True)
       
    def save_uploaded_files(self, reference_file, actual_file):
        try:
            reference_path = self.session_path / reference_file.name
            actual_path = self.session_path / actual_file.name
            
            for file_obj, out in ((reference_file, reference_path), (actual_file, actual_path)):
                if not file_obj.name.lower().endswith(".pdf"):
                    raise ValueError("Only PDF files are allowed.")
                
                with open(out, "wb") as file:
                    if hasattr(file_obj, "read"):
                        file.write(file_obj.read())
                    else:
                        file.write(file_obj.getbuffer())
                        
            return reference_path, actual_path
        except Exception as e:
            raise DocumentQueryingPortalException("Error saving files", e) 

    def read_pdf(self, pdf_path: Path) -> str:
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                
                parts = []
                
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text() 
                    
                    if text.strip():
                        parts.append(f"\n --- Page {page_num + 1} --- \n{text}")
                        
            return "\n".join(parts)
        except Exception as e:
            raise DocumentQueryingPortalException("Error reading PDF", e) 

    def combine_documents(self) -> str:
        try:
            doc_parts = []
            
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() == ".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")
                    
            combined_text = "\n\n".join(doc_parts)
            
            return combined_text
        except Exception as e:
            raise DocumentQueryingPortalException("Error combining documents", e) 

    def clean_old_sessions(self, keep_latest: int = 3):
        try:
            sessions = sorted([f for f in self.base_dir.iterdir() if f.is_dir()], reverse=True)
            
            for folder in sessions[keep_latest:]:
                shutil.rmtree(folder, ignore_errors=True)
        except Exception as e:
            raise DocumentQueryingPortalException("Error cleaning old sessions", e) 

class DocumentIngestor:
    def __init__( self,
        temp_base: str = "data",
        faiss_base: str = "faiss_index",
        use_session_dirs: bool = True,
        session_id: Optional[str] = None,
    ):
        try:
            self.model_loader = ModelLoader()
            
            self.use_session = use_session_dirs
            self.session_id = session_id or generate_session_id()
            
            self.temp_base = Path(temp_base); self.temp_base.mkdir(parents=True, exist_ok=True)
            self.faiss_base = Path(faiss_base); self.faiss_base.mkdir(parents=True, exist_ok=True)
            
            self.temp_dir = self.__resolve_dir(self.temp_base)
            self.faiss_dir = self.__resolve_dir(self.faiss_base)

        except Exception as e:
            raise DocumentQueryingPortalException("Initialization error in ChatIngestor", e)
            
    def __resolve_dir(self, base: Path):
        if self.use_session:
            directory = base / self.session_id 
            directory.mkdir(parents=True, exist_ok=True) 
            return directory
        return base
        
    def __split(self, docs: List[Document], chunk_size=1000, chunk_overlap=200) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(docs)
    
    def built_retriver( 
        self,
        uploaded_files: Iterable,
        *,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        k: int = 5,):
        try:
            paths = save_uploaded_files(uploaded_files, self.temp_dir)
            docs = load_documents(paths)
            if not docs:
                raise ValueError("No valid documents loaded")
            
            chunks = self.__split(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            faiss_manager = FaissManager(self.faiss_dir, self.model_loader)
            
            texts = [chunk.page_content for chunk in chunks]
            metas = [chunk.metadata for chunk in chunks]
            
            vector_store = faiss_manager.load_or_create(texts=texts, metadatas=metas)
                
            added = faiss_manager.add_documents(chunks)
            
            return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
            
        except Exception as e:
            raise DocumentQueryingPortalException("Failed to build retriever", e)