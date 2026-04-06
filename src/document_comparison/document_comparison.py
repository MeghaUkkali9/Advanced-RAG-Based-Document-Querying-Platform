import sys
from dotenv import load_dotenv
import pandas as pd

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentQueryingPortalException
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

log = CustomLogger().get_logger(__name__)

class DocumentComparatorLLM:
    def __init__(self):
        load_dotenv()
        log.info("Initializing DocumentComparator...")
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.output_parser = OutputFixingParser.from_llm(
            llm=self.llm,
            parser=self.parser
        )

        self.prompt = PROMPT_REGISTRY["document_comparison"]
        self.chain = self.prompt | self.llm | self.output_parser

        log.info("DocumentComparator initialized successfully")

    def compare_documents(self, combined_docs:str):
        """Compare the two documents and return the differences."""
        try:
            input_data = {
                "combined_document": combined_docs,
                "format_instructions": self.parser.get_format_instructions()
            }

            log.info("Comparing documents using LLM...")
            response = self.chain.invoke(input_data)
            log.info("Document comparison completed successfully")
            return self._format_response(response)
        except Exception as e:
            log.error(f"Error comparing documents: {e}")
            raise DocumentQueryingPortalException("Failed to compare documents", sys)

    def _format_response(self, response:list[dict]) -> pd.DataFrame:
        """Format the response from the LLM to be user-friendly."""
        try:
            df = pd.DataFrame(response)
            log.info("Response formatted successfully")
            return df
        except Exception as e:
            log.error(f"Error formatting response: {e}")
            raise DocumentQueryingPortalException("Failed to format response", sys)

