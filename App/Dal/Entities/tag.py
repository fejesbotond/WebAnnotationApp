from pydantic import BaseModel


class Tag(BaseModel):
    id: str
    value: str
