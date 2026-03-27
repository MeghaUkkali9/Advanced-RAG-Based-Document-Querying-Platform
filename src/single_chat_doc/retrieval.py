import sys
import os
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableChatMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrival_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType
from utils.model_loader import ModelLoader

class ConversationalRetrieval:
    def __init__(self, session_id:str=None, retriever:FAISS=None) -> None:
        try:
            load_dotenv()
            self.log = CustomLogger().get_logger(__name__)
            self.model_loader = ModelLoader()
            self.session_id = session_id
            self.retriever = retriever
        except Exception as e:
            self.log.error(f"Error initializing ConversationalRetrieval: {e}")
            raise DocumentQueryingPortalException("Failed to initialize ConversationalRetrieval", sys) from e

    def _load_llm(self):
        try:
            llm = self.model_loader.load_llm()
            self.log.info("LLM loaded successfully")
            return llm
        except Exception as e:
            self.log.error(f"Error loading LLM: {e}")
            raise DocumentQueryingPortalException("Failed to load LLM", sys)
    
    def _get_session_history(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error getting session history: {e}")
            raise DocumentQueryingPortalException("Failed to get session history", sys)

    def load_retriever_from_faiss(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error loading retriever from FAISS: {e}")
            raise DocumentQueryingPortalException("Failed to load retriever from FAISS", sys)
        
    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error(f"Error invoking conversational retrieval: {e}")
            raise DocumentQueryingPortalException("Failed to invoke conversational retrieval", sys) 
        