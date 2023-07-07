from datetime import datetime
from typing import List

from pydantic import BaseModel
from Dtos.annotation import Annotation
from Dtos.create_document import CreateDocument
from Dtos.relation import Relation


class Document(BaseModel):
    relations: List[Relation]
    annotations: List[Annotation]
    title: str
    content: str

class DocumentInfo(BaseModel):
    id: str
    title: str
    file_name: str
    date: datetime
    count_annotations: int

