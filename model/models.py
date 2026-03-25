from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union

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
    changes: str

class SummaryResponse(RootModel[list[ChangeFormat]]): 
    pass

