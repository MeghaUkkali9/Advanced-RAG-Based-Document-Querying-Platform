from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Document(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Query(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    sort: Optional[List[str]] = None

class Response(BaseModel):
    documents: List[Document]
    total: int