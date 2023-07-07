from datetime import datetime
from typing import List

from fastapi import UploadFile
from Dal.Entities.annotation import Annotation
from Dal.Entities.document import Document
from Dal.Entities.relation import Relation
from Dtos.create_annotation import CreateAnnotation
from Dtos.document import Document as DocumentResponse, CreateDocument
from Dtos.annotation import Annotation as AnnotationResponse
from Dtos.relation import CreateRelation, Relation as RelationResponse, ResponseBodyItem, TargetItem

class AnnotationParser:
    def db_to_response(self, annotation: Annotation) -> AnnotationResponse:
        db_obj = annotation.dict()
        result = {}
        result["id"] = db_obj["id"]
        result["type"] = "Annotation"
        result["document_id"] = db_obj["document_id"]
        result["body"] = []
        for item in db_obj["comments"]:
            result["body"].append({
                "type": "TextualBody",
                "value": item,
                "purpose": "commenting"
            })
        
        for item in db_obj["tags"]:
            result["body"].append({
                "type": "TextualBody",
                "value": item,
                "purpose": "tagging"
            })

        result["target"] = {}
        result["target"]["selector"] = []
        result["target"]["selector"].append({
            "type": "TextQuoteSelector",
            "exact": db_obj["text"]
        })
        result["target"]["selector"].append({
            "type": "TextPositionSelector",
            "start": db_obj["location"]["start"],
            "end": db_obj["location"]["end"]
        })
        return AnnotationResponse(**result)
    
    def request_to_db(self, annotation: CreateAnnotation) -> Annotation:
        data = annotation.dict()
        result= {}
        for item in data["target"]["selector"]:
            if ("exact" not in item):
                result["location"] = {}
                result["location"]["start"] = item["start"]
                result["location"]["end"] = item["end"]
            else:
                result["text"] = item["exact"]
        
        result["comments"] = [item["value"] for item in data["body"] if item["purpose"] == "commenting"]
        result["tags"] = [item["value"] for item in data["body"] if item["purpose"] == "tagging"]
        result["document_id"] = data["document_id"]
        return Annotation(**result)


class RelationParser:
    def db_to_response_relation(self, db_relation: Relation) -> RelationResponse:
        body: List[ResponseBodyItem] = []
        for item in db_relation.tags:
            body.append(ResponseBodyItem(value=item, type="TextualBody",purpose="tagging"))
        
        target: List[TargetItem] = []
        target.append(TargetItem(id=db_relation.id_from))
        target.append(TargetItem(id=db_relation.id_to))

        return RelationResponse( id= db_relation.id, type="Annotation", motivation="linking", body=body, target=target)

    def request_to_db_relation(self, create_relation: CreateRelation) -> Relation:
        relation_tags = []
        for item in create_relation.body:
            if item.value not in relation_tags:
                relation_tags.append(item.value)
        return Relation(id_from=create_relation.target[0].id, id_to=create_relation.target[1].id,
                         document_id=create_relation.document_id, tags=relation_tags)
    
class DocumentParser:

    def __init__(self, parser: AnnotationParser, parserR: RelationParser):
        self.annotation_parser = parser
        self.relation_parser = parserR

    def db_to_response_annotations(self, db_annotations: List[Annotation]) -> List[AnnotationResponse]:
        result = []
        for item in db_annotations:
            result.append(self.annotation_parser.db_to_response(item))
        return result

    def db_to_response_relations(self, db_relations: List[Relation]) -> List[RelationResponse]:
        result = []
        for item in db_relations:
            result.append(self.relation_parser.db_to_response_relation(item))
        return result

    def request_to_db(self, file: UploadFile, title: str) -> Document:
        result = Document(title=title, date=datetime.now(), annotations=[], relations=[], file_name=file.filename)
        return result
    


    







