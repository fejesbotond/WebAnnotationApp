from typing import List
from pydantic import BaseModel, Field

class BodyItem(BaseModel):
    value: str  


class TargetItem(BaseModel):
    id: str


class CreateRelation(BaseModel):
    body: List[BodyItem] = Field(..., min_items=1)
    target: List[TargetItem] = Field(..., min_items=2, max_items=2)
    document_id: str


class ResponseBodyItem(BodyItem):
    type: str
    purpose: str

class Relation(BaseModel):
    id: str
    type: str
    motivation: str
    body: List[ResponseBodyItem]
    target: List[TargetItem]
