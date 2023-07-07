import codecs
from datetime import datetime
import os
from typing import List, Optional

from fastapi import Request, UploadFile
from Dal.Repositories.document_repo import DocumentRepository
from Dal.Entities.document import Document as DocumentEntity
from Dtos.create_document import CreateDocument
from Dtos.document import Document, DocumentInfo
from Dtos.document import Document as ResponseDocument
from Services.parsers import DocumentParser
from Services.service import Service, get_file_content
from bson import ObjectId


class DocumentService(Service):

    def __init__(self, repository: DocumentRepository, parser: DocumentParser):
        self.repository = repository
        self.parser = parser

   
    
    def list_documents(self) -> List[DocumentInfo]:
        return self.repository.get_documents()
    

    def get_document_with_annotations(self, id: str) -> Optional[ResponseDocument]:
        if(not self.validate_id(id)):
            return None
        doc = self.repository.get_one_document(id)
        if(doc is None):
            return None
        annotations = self.parser.db_to_response_annotations(doc.annotations)
        relations = self.parser.db_to_response_relations(doc.relations)
        res = ResponseDocument(relations=relations,  annotations=annotations, title=doc.title, content=get_file_content(id))
        print(res)
        return res



    def add_document(self,file: UploadFile, title: str) -> Optional[DocumentInfo]:
        if(len(title) == 0):
            return None
        if(file.size == 0 or file.size > 1000000*5):
            return None
        contents = file.file.read()
        print(str(contents))
        try:
            contents.decode("utf-8")
        except UnicodeDecodeError as e:
            print(e)
            return None
        db_doc = self.parser.request_to_db(file, title) 
        doc_response = self.repository.add_document(db_doc)
        if doc_response is None:
            return None
        file_path = f"resources/files/{doc_response.id}.txt"
        with open(file_path, "wb") as f:
            f.write(contents)
        return doc_response
        

    def delete_one_document(self, id: str) -> bool:
        if not self.validate_id(id):
            return False
        db_delete: bool = self.repository.del_document(id)
        if(not db_delete):
            return False
        file_path = f"resources/files/{id}.txt"

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("file does not exist")
        return True
        