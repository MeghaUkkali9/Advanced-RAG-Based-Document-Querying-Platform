from utils.model_loader import ModelLoader
from logger.logger_instance import logger as log
from exception.custom_exception import DocumentQueryingPortalException
from model.models import *
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import PROMPT_REGISTRY

class DocumentAnalyzer:
    """
    Analyzes documents using a pre-trained model and parses the output.
    """ 
    def __init__(self):
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            self.parser = JsonOutputParser(pydantic_object=MetaData)
            self.fixing_parser = OutputFixingParser.from_llm(llm=self.llm, parser=self.parser)

            self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_ANALYSIS]

            log.info("DataAnalyzer initialized successfully")

        except Exception as e:
            log.error(f"Error initializing DataAnalyzer: {e}")
            raise DocumentQueryingPortalException("Failed to initialize DataAnalyzer", e) from e

    def analyze_document(self, document_text: str) -> dict:
        try:
            chain = self.prompt | self.llm | self.fixing_parser
            log.info(f"Analyzing document: {document_text[:100]}...") 

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            log.info(f"Document analysis completed successfully: {response}")
            return response
        
        except Exception as e:
            log.error(f"Error analyzing document: {e}")
            raise DocumentQueryingPortalException("Failed to analyze document", e) from e