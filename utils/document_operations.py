from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
from fastapi import UploadFile
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentQueryingPortalException

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def load_documents(paths: Iterable[Path]) -> List[Document]:
    """
    Load docs using appropriate loader based on extension.
    """
    docs: List[Document] = []
    
    try:
        for path in paths:
            ext = path.suffix.lower()
            
            if ext == ".pdf":
                loader = PyPDFLoader(str(path))
            elif ext == ".docx":
                loader = Docx2txtLoader(str(path))
            elif ext == ".txt":
                loader = TextLoader(str(path), encoding="utf-8")
            else:
                log.warning("Unsupported extension skipped", path=str(path))
                continue
            
            docs.extend(loader.load())
            
            
        log.info("Documents loaded", count=len(docs))
        return docs
    except Exception as e:
        log.error("Failed loading documents", error=str(e))
        raise DocumentQueryingPortalException("Error loading documents", e)

def concat_for_analysis(docs: List[Document]) -> str:
    parts = []
    
    for doc in docs:
        src = doc.metadata.get("source") or doc.metadata.get("file_path") or "unknown"
        parts.append(f"\n--- SOURCE: {src} ---\n{doc.page_content}")
        
    return "\n".join(parts)

def concat_for_comparison(ref_docs: List[Document], act_docs: List[Document]) -> str:
    left = concat_for_analysis(ref_docs)
    right = concat_for_analysis(act_docs)
    return f"<<REFERENCE_DOCUMENTS>>\n{left}\n\n<<ACTUAL_DOCUMENTS>>\n{right}"
