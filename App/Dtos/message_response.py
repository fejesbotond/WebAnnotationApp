from pydantic import BaseModel


class ResponseCreated(BaseModel):
    message: str
    id: str

class ResponseMessage(BaseModel):
    message: str