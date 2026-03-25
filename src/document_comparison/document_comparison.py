import sys
from dotenv import load_dotenv
import pandas as pd

from logger.custom_logger import logger as log
from exception.custom_exception import DocumentQueryingPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentComparator:
    def __init__(self):
        self.llm = ModelLoader().load_llm()

    def compare_documents(self):
        """Compare the two documents and return the differences."""
        pass

    def format_response(self):
        """Format the response from the LLM to be user-friendly."""
        pass

