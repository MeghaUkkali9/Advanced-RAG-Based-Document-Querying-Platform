from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MetaData(BaseModel):
    Summary: List[str] = Field(..., description="A list of summary sentences extracted from the document.")
    Title: str
    Author: str
    DateCreated: str
    LastModified: str
    Publisher: str
    PageCount: int
    Sentiment: str
