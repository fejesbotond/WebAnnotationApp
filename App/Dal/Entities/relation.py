from typing import List, Optional
from pydantic import BaseModel



class Relation(BaseModel):
    id: Optional[str]
    id_from: str
    id_to: str
    document_id: str
    tags: List[str]
    