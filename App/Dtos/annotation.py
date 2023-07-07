from typing import List, Union
from pydantic import BaseModel, Field, validator
from Dtos.create_annotation import BodyItem, ExactText, TextPosition


class BodyResponseItem(BodyItem):
    type: str
    @validator('type')
    def match(cls, v):
        if v != "TextualBody":
            raise ValueError('types value must be TextualBody')
        return v



class TextPositionResponse(TextPosition):
    type: str
    @validator('type')
    def match(cls, v):
        if v != "TextPositionSelector":
            raise ValueError('types value must be TextPositionSelector')
        return v

class ExactTextResponse(ExactText):
    type: str
    @validator('type')
    def match(cls, v):
        if v != "TextQuoteSelector":
            raise ValueError('types value must be TextQuoteSelector')
        return v

class SelectorArrayResponse(BaseModel):
    selector: List[Union[TextPositionResponse, ExactTextResponse]] = Field(..., min_items=2, max_items=2)
    
    @validator('selector')
    def validate_selector(cls, selector):
        if not ((isinstance(selector[0], TextPositionResponse) and isinstance(selector[1], ExactTextResponse)) or
               (isinstance(selector[0], ExactTextResponse) and isinstance(selector[1], TextPositionResponse))):
            raise ValueError('selector must contain one TextPosition and one ExactText, with order not mattering')
        return selector
    
class Annotation(BaseModel):
    id: str
    type: str
    body: List[BodyResponseItem]
    target: SelectorArrayResponse
    document_id: str

    @validator('type')
    def match(cls, v):
        if v != "Annotation":
            raise ValueError('types value must be Annotation')
        return v