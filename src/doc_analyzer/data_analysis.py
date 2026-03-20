import os
from utils.model_loader import ModelLoader
from logger.logger_instance import logger as log
from exception.custom_exception import DocumentQueryingPortalException
from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DataAnalyzer:
    """
    Analyzes documents using a pre-trained model and parses the output.
    """ 
    def __init__(self, data: dict):
        pass

    def analyze_metadata(self, document_path: str):
        try:
            # Load the model
            model = self.model_loader.load_model("data-analyzer")
            log.info("Model loaded successfully")

            # Analyze the data
            results = model.analyze(document_path)
            log.info("Data analyzed successfully")

            # Parse the output
            parsed_results = self.fixing_parser.parse(results)
            log.info("Output parsed successfully")

            return parsed_results
        
        except Exception as e:
            log.error(f"Error analyzing data: {e}")
            raise DocumentQueryingPortalException("Failed to analyze data")