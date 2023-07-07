from typing import List
from pydantic import BaseModel


class UpdateAnnotation(BaseModel):
    comments: List[str]
    tags: List[str]
