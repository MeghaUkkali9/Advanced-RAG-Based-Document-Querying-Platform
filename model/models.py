from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class MetaData(BaseModel):
    Summary: List[str] = Field(..., description="A list of summary sentences extracted from the document.")
    Title: str
    Author: str
    DateCreated: str
    LastModified: str
    Publisher: str
    Language: str
    PageCount: Union[int, str]
    SentimentTone: str

class ChangeFormat(BaseModel):
    Page: str
    added: List[str]
    deleted: List[str]

class SummaryResponse(RootModel[list[ChangeFormat]]): 
    pass

class PromptType(str, Enum):
    DOCUMENT_ANALYSIS = "document_analysis"
    DOCUMENT_COMPARISON = "document_comparison"
    CONTEXTUALIZE_QUERY = "contextualize_query"
    CONTEXT_QUERY_ANSWERING = "context_query_answering"

