from typing import List, Union
from pydantic import BaseModel, Field, validator


class BodyItem(BaseModel):
    value: str
    purpose: str

    @validator('purpose')
    def validate_purpose(cls, p):
        if(p != "commenting" and p != "tagging"):
            raise ValueError("Purpose key value has to be [commenting] or [tagging]")
        return p

class ExactText(BaseModel):
    exact: str

class TextPosition(BaseModel):
    start: int
    end: int

class SelectorArray(BaseModel):
    selector: List[Union[TextPosition, ExactText]] = Field(..., min_items=2, max_items=2)
    
    @validator('selector')
    def validate_selector(cls, selector):
        if not ((isinstance(selector[0], TextPosition) and isinstance(selector[1], ExactText)) or
               (isinstance(selector[0], ExactText) and isinstance(selector[1], TextPosition))):
            raise ValueError('selector must contain one TextPosition and one ExactText, with order not mattering')
        return selector

class CreateAnnotation(BaseModel):
    body: List[BodyItem] = Field(..., min_items=1)
    target: SelectorArray
    document_id: str