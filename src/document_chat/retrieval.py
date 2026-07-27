import os

from dotenv import load_dotenv
from operator import itemgetter
from typing import List, Optional, Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
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
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self.__load_llm()
            self.contextualize_prompt: ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUERY.value]
            self.qa_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QUERY_ANSWERING.value]

            self.retriever = retriever
            self.chain = None
            
            self.log.info("Initialized ConversationalRAG")
        except Exception as e:
            self.log.info("Error while initializing", e)
            raise DocumentQueryingPortalException("Initializing error in ConversationalRAG", e) from e

    def load_retriever_from_faiss(
        self, 
        index_path:str,
        k: int = 5,
        index_name: str = "index",
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None):
        """
        Load a FAISS vector store from disk and convert to retriever
        """
        try:
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            embeddings = ModelLoader().load_embeddings()
            
            vector_store = FAISS.load_local(
                index_path,
                embeddings,
                index_name = index_name,
                allow_dangerous_deserialization=True
            )
            
            if search_kwargs is None:
                search_kwargs = {"k": k}
                
            self.retriever = vector_store.as_retriever(
                search_type= search_type, 
                search_kwargs= search_kwargs
                )
            self.log.info("FAISS retriever loaded successfully", index_path=index_path, session_id=self.session_id)
            
            self.__build_lcel_chain()
            
            return self.retriever
        
        except Exception as e:
            raise DocumentQueryingPortalException("Loading Error in ConversationalRAG", e) from e

    def invoke(self, user_input, chat_history: Optional[List[BaseMessage]] = None) -> str:
        """
        Args:
            user_input (str): _description_
            chat_history (Optional[List[BaseMessage]], optional): _description_. Defaults to None
        """
        try:
            if self.chain is None:
                raise ValueError("Chain not initialized. Call load_retriever_from_faiss first.")

            chat_history = chat_history or []
            payload = {
                "input": user_input,
                "chat_history": chat_history
            }
            answer = self.chain.invoke(payload)

            if not answer:
                self.log.warning("Empty answer received", session_id= self.session_id)
                return "No answer generated"
            
            self.log.info("Chain invoked successfully", session_id=self.session_id, user_input=user_input, answer_previous=answer[:150])
            return answer
        except Exception as e:
            self.log.error(f"Error invoking conversational retrieval: {e}")
            raise DocumentQueryingPortalException("Failed to invoke in ConversationalRAG", e) from e

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)

    def __build_lcel_chain(self):
        try:
            if self.retriever is None:
                raise ValueError("Retriever not initialized. Cannot build chain.")

            question_rewriter = (
                { "input": itemgetter("input"), "chat_history": itemgetter("chat_history")}
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser()
            )

            retrieve_docs = question_rewriter | self.retriever | self.format_docs
            # retrieve_docs = self.retriever | RunnablePassthrough(
            #     input_key = "input",
            #     output_key = "context"
            # )
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
            raise DocumentQueryingPortalException("LCEL Chain building Error in ConversationalRAG", e) from e

    def __load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM could not be loaded")
            
            self.log.info("LLM is loaded successfully", session_id = self.session_id)
            return llm
        except Exception as e:
            raise DocumentQueryingPortalException("Invoking Error in ConversationalRAG", e) from e
            



