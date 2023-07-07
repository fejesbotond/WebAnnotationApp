from datetime import datetime
from http.client import HTTPResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Annotated, List
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel
from Dtos.annotation import Annotation
from Dtos.create_document import CreateDocument
from Dtos.create_annotation import CreateAnnotation
from Dtos.document import Document, DocumentInfo
from Dtos.message_response import ResponseCreated, ResponseMessage
from Dtos.relation import CreateRelation
from Dtos.tags import Tag, Tags
from Dtos.update_annotation import UpdateAnnotation
from Services.Annotation.annotation_service import AnnotationService

from Services.Document.document_service import DocumentService
from Services.Relation.relation_service import RelationService
from Services.Tags.tags_service import TagsService
from Services.entity_recog_service import EntityRecognitionService
from Services.get_services import get_annotation_service, get_document_service, get_entity_recognition_service, get_relation_service, get_tags_service

routes = APIRouter()


@routes.get("/documents", response_model=List[DocumentInfo])
def get_documents(service: DocumentService = Depends(get_document_service)):
    return service.list_documents()


@routes.get("/documents/{id}", response_model=Document)
def get_one_document(id: str, service: DocumentService = Depends(get_document_service)):
    result = service.get_document_with_annotations(id)
    print(result.relations)
    if(result is None): 
        raise HTTPException(detail="No such document", status_code=404)
    return result


@routes.post("/documents", response_model=DocumentInfo)
def add_document(file: UploadFile = File(...), title: str = Form(...), service: DocumentService = Depends(get_document_service)):
    doc = service.add_document(file, title)
    if(doc is None):
        raise HTTPException(detail="Something went wrong with the insertion.", status_code=404)
    return doc


@routes.delete("/documents/{id}", response_model=ResponseMessage)
def delete_document(id: str, service: DocumentService = Depends(get_document_service)):
    result = service.delete_one_document(id)
    if(result == False):
        raise HTTPException(detail="Delete operation failed.", status_code=404)
    return {"message": "Successful delete."}


@routes.post("/annotations", response_model=ResponseCreated)
def add_annotation(annotation: CreateAnnotation,
                    service: AnnotationService = Depends(get_annotation_service)):
    result = service.add_annotation(annotation)
    if(result["annotation_id"] is None):
        raise HTTPException(detail=result["message"], status_code=404)
    return {"message": "Annotation added successfully.", "id": result["annotation_id"]}


@routes.delete("/annotations/{id}", response_model=ResponseMessage)
def delete_annotation(id: str, service: AnnotationService = Depends(get_annotation_service)):
    result = service.delete_one_annotation(id)
    if(result == False):
        raise HTTPException(detail="Delete annotation failed.", status_code=404)
    return {"message": "Successful delete."}


@routes.patch("/annotations/{id}", response_model=ResponseMessage)
def update_annotation(id: str, changes: UpdateAnnotation, service: AnnotationService=Depends(get_annotation_service)):
    result = service.update_annotation(id, changes)
    if not result:
        raise HTTPException(detail="Update operation failed.", status_code=404)
    return {"message": "Successful update."}

@routes.post("/relations", response_model=ResponseCreated)
def add_relation(item: CreateRelation, service: RelationService=Depends(get_relation_service)):
    result = service.add_relation(item)
    if(result["annotation_id"] is None):
        raise HTTPException(detail=result["message"], status_code=404)
    return {"message": result["message"], "id": result["annotation_id"]}


@routes.delete("/relations/{id}", response_model=ResponseMessage)
def delete_relation(id: str, service: RelationService=Depends(get_relation_service)):
    result = service.delete_relation(id)
    if result == False:
        raise HTTPException(detail="Delete relation failed.", status_code=404)
    return {"message": "Successful relation delete"}
    

@routes.patch("/relations/{id}", response_model=ResponseMessage)
def update_relation(id: str, tag: Tag, service: RelationService=Depends(get_relation_service)):
    result = service.update_relation(id, tag.tag)
    if result == False:
        raise HTTPException(detail="Updating relation failed.", status_code=404)
    return {"message": "Successful relation update."}

@routes.get("/entity_tags", response_model=List[str])
def get_tags(service: TagsService=Depends(get_tags_service)):
    return service.get_entity_tags()


@routes.get("/relation_tags", response_model=List[str])
def get_tags(service: TagsService=Depends(get_tags_service)):
    return service.get_relation_tags()


@routes.post("/documents/{id}/spacy-ai", response_model=List[Annotation])
def run_spacy_recognition(id: str, service: EntityRecognitionService=Depends(get_entity_recognition_service)):
   res =  service.run_spacy_ner(id)
   if res is None:
       raise HTTPException(detail="Something went wrong", status_code=400)
   return res
    


@routes.get("/document", response_class=HTMLResponse)
def get_document_html(id: str):
    with open("static/annotations.html", "r") as f:
        return f.read()


@routes.get("/", response_class=HTMLResponse)
async def read_index():
    with open("static/index.html", "r") as f:
        return f.read()
