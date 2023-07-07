from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from Dal.Entities.annotation import Annotation
from Dal.Entities.relation import Relation

class Document(BaseModel):
    id: Optional[str]
    title: str
    file_name: str
    date: datetime
    annotations: List[Annotation]
    relations: List[Relation]