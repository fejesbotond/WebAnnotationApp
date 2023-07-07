from typing import List, Optional
from pydantic import BaseModel



class Location(BaseModel):
    start: int
    end: int


class Annotation(BaseModel):
    id: Optional[str]
    comments: List[str]
    tags: List[str]
    document_id: str
    location: Location
    text: str
    