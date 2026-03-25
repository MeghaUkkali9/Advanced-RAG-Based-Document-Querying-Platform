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
        load_dotenv()
        log.info("Initializing DocumentComparator...")
        self.loader = ModelLoader()
        self.llm = self.loader.load_model()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.output_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=self.parser
        )

        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.output_parser

        log.info("DocumentComparator initialized successfully")

    def compare_documents(self):
        """Compare the two documents and return the differences."""
        try:
            pass
        except Exception as e:
            log.error(f"Error comparing documents: {e}")
            raise DocumentQueryingPortalException("Failed to compare documents", sys)

    def _format_response(self):
        """Format the response from the LLM to be user-friendly."""
        try:
            pass
        except Exception as e:
            log.error(f"Error formatting response: {e}")
            raise DocumentQueryingPortalException("Failed to format response", sys)

