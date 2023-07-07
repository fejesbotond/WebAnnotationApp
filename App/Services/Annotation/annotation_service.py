from typing import List, Optional
from Dal.Entities.annotation import Annotation
from Dal.Repositories.annotation_repo import AnnotationRepository
from Dal.Repositories.document_repo import DocumentRepository
from Dal.Repositories.tags_repo import TagsRepository
from Dtos.create_annotation import CreateAnnotation
from Dtos.create_document import CreateDocument
from Dal.Entities.document import Document
from Dtos.update_annotation import UpdateAnnotation
from Services.parsers import AnnotationParser
from Services.service import Service, get_file_content
from bson import ObjectId


class AnnotationService(Service):
    def __init__(self, repository_a: AnnotationRepository, repository_d: DocumentRepository, repository_t: TagsRepository, parser: AnnotationParser):
        self.repository_annotation = repository_a
        self.repository_doc = repository_d
        self.repository_tags = repository_t
        self.parser = parser

    def validate_tags(self, tags: List[str], db_tags: List[str]) -> bool:
        for item in tags:
            if item not in db_tags:
                return False
        return True

    def delete_one_annotation(self, id: str) -> bool:
        if(not self.validate_id(id)):
            return False
        return self.repository_annotation.del_annotation(id)
    
    def update_annotation(self, id: str, changes: UpdateAnnotation) -> bool:
        if(not self.validate_id(id)):
            return False
        if len(changes.comments) == 0 and len(changes.tags) == 0:
            return False
        
        if not self.validate_tags(changes.tags, self.repository_tags.get_tags()):
            return False
        
        obj = UpdateAnnotation(comments=changes.comments, tags=set(changes.tags))
        return self.repository_annotation.update_annotation(id, obj)

    def add_annotation(self, new_annotation: CreateAnnotation):
        data = new_annotation.dict()
        if(not self.validate_id(data["document_id"])):
            return {"message": "No such document.", "annotation_id": None}
        document = self.repository_doc.get_one_document(data["document_id"])
        if(document is None):
            return {"message": "No such document.", "annotation_id": None}
        
        document = document.dict()
        exact_text = None
        start_value = None
        end_value = None
        for item in data["target"]["selector"]:
            if ("exact" not in item):
                start_value = item["start"]
                end_value = item["end"]
            else:
                exact_text = item["exact"]

        
        if(start_value is None or end_value is None):
            return {"message": "Incorrect selectors", "annotation_id": None}
        
        content = get_file_content(data["document_id"])

        if(content[start_value:end_value] != exact_text):
            return {"message": "Inconsistent selectors.", "annotation_id": None}
        
        new_tags: List[str] = []
        for item in data["body"]:
            if(item["purpose"] == "tagging" and (item["value"] not in new_tags)):
                new_tags.append(item["value"])

        if not self.validate_tags(new_tags, self.repository_tags.get_tags()):
            return {"message": "Invalid Tags", "annotation_id": None}
        
        obj: Annotation = self.parser.request_to_db(new_annotation)
        obj.tags = new_tags[:]

        result = self.repository_annotation.add_annotation(obj)
        
        if(result is None):
             return {"message": "Insertion failed.", "annotation_id": None}
        
        return {"message": "Succesful insertion.", "annotation_id": result}
        

