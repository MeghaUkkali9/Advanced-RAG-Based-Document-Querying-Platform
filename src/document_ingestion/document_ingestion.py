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
from langchain_community.document_logging import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstore import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException

from utils.file_io import __session_io, save_uploaded_files
from utils.document_operations import load_documents, concat_for_analysis, concat_for_comparison

class FaissManager:
    def __init__(self):
        pass

    def load_or_create(self):
        pass
    
    def add_documents(self):
        pass
    
    def __exists(self):
        pass
    
    @staticmethod
    def __finger_print(self):
        pass
    
    def __save_metadata(self):
        pass
     
class DocumentHandler:
    def __init__(self):
        pass
    
    def save_pdf(self):
        pass
    
    def read_pdf(self):
        pass
    

class DocuementComparator:
    def __init__(self):
        pass
    
    def save_uploaded_files(self):
        pass
    
    def read_pdf(self):
        pass
    
    def combine_documents(self):
        pass
    
    def clean_old_sessions(self):
        pass

class DocumentIngestor:
    def __init__(self):
        pass
    
    def __resolve_dir(self):
        pass
    
    def __split(self):
        pass
    
    def build_retriver(self):
        pass