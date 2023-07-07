from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel


class CreateDocument(BaseModel):
    title: str
    file: UploadFile
    date: str