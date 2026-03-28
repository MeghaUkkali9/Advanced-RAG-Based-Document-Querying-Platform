import sys
import os

from dotenv import load_dotenv
from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parser import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG:
    def __init__(self, session_id:str, retriever=None):
        try:
            self.log = CustomLogger.get_logger(__name__)
            self.session_id = session_id
            self.llm = self.__load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUERY.value]
            self.qa_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QUERY_ANSWERING.value]

            if retriever is None:
                raise ValueError("retreiver is not assigned")
            
            self.retriever = retriever
            self.__build_lcel_chain()

            self.log.info("Initialized ConversationalRAG")
        except Exception as e:
            self.log.info("Error while initializing", e)
            raise DocumentQueryingPortalException("Initializing error in ConversationalRAG", sys)

    def load_retriever_from_faiss(self, index_path:str):
        try:
            embeddings = ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            vector_store = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True
            )

            self.retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k":5})
            self.log.info("FAISS retriever loaded successfully", index_path=index_path, session_id=self.session_id)

            self.__build_lcel_chain()
            return self.retriever
        
        except Exception as e:
            raise DocumentQueryingPortalException("Loading Error in ConversationalRAG", sys)

    def invoke(self):
        try:
            pass
        except Exception as e:
            raise DocumentQueryingPortalException("Invoking Error in ConversationalRAG", sys)

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    def __build_lcel_chain(self):
        try:
            retrieve_docs = self.retriever | RunnablePassthrough(
                input_key = "input",
                output_key = "context"
            )
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            
        except Exception as e:
            self.log.info("Failed to build LCEL Chain")
            raise DocumentQueryingPortalException("LCEL Chain building Error in ConversationalRAG", sys)

    def __load_llm(self):
        try:
            llm = ModelLoader.load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            
            self.log.info("LLM is loaded successfully", session_id = self.session_id)
            return llm
        except Exception as e:
            raise DocumentQueryingPortalException("Invoking Error in ConversationalRAG", sys)



