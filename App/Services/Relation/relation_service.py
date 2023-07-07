from typing import Optional
from Dal.Repositories.annotation_repo import AnnotationRepository
from Dal.Repositories.document_repo import DocumentRepository
from Dal.Repositories.relation_repo import RelationRepository
from Dal.Repositories.tags_repo import TagsRepository
from Dtos.message_response import ResponseMessage
from Dtos.relation import CreateRelation
from Services.parsers import RelationParser
from Services.service import Service


class RelationService(Service):
    def __init__(self, repoRel: RelationRepository, repoDoc: DocumentRepository, repoTag: TagsRepository, repoAnn: AnnotationRepository, parser: RelationParser) -> None:
        self.relation_repository = repoRel
        self.document_repository = repoDoc
        self.tag_repository = repoTag
        self.annotation_repository = repoAnn
        self.parser = parser

    def add_relation(self, new_relation: CreateRelation):
        if not self.validate_id(new_relation.document_id):
            return {"message": "invalid document id", "annotation_id": None}
        
        if not self.validate_id(new_relation.target[0].id):
            return {"message": "invalid from_id", "annotation_id": None}
        
        if not self.validate_id(new_relation.target[1].id):
            return {"message": "invalid to_id", "annotation_id": None}
        
        document = self.document_repository.get_one_document(new_relation.document_id)
        if document is None:
            return {"message": "No such document.", "annotation_id": None}
        
        from_annotation = self.annotation_repository.get_one_annotation(new_relation.target[0].id)
        if from_annotation is None:
            return {"message": "No such from_id.", "annotation_id": None}
        
        if from_annotation.document_id != new_relation.document_id:
            return {"message": "From_Annotation is not in the document", "annotation_id": None} 
        
        to_annotation = self.annotation_repository.get_one_annotation(new_relation.target[1].id)
        if to_annotation is None:
            return {"message": "No such to_id.", "annotation_id": None}
        
        if to_annotation.document_id != new_relation.document_id:
            return {"message": "To_Annotation is not in the document", "annotation_id": None} 
        
        relation_tags = self.tag_repository.get_relation_tags()

        for item in new_relation.body:
            if item.value not in relation_tags:
                return {"message": "Invalid Tags", "annotation_id": None}
        
        db_relation = self.parser.request_to_db_relation(new_relation)
        inserted_id = self.relation_repository.add_relation(db_relation)
        if inserted_id is None:
            return {"message": "Falied insertion", "annotation_id": None}
        
        return {"message": "Successful relation insertion.", "annotation_id": inserted_id}
    
    def delete_relation(self, id: str) -> bool:
        if not self.validate_id(id):
            return False
        res = self.relation_repository.del_relation(id)
        return res
    
    def update_relation(self, id: str, tag: str) -> bool:
        if not self.validate_id(id):
            return False
        
        relation_tags = self.tag_repository.get_relation_tags()

        if tag not in relation_tags:
            return False
        
        return self.relation_repository.update_relation(id, tag)
        
        