from typing import List, Optional
from Dal.Entities.annotation import Annotation
from Dal.Entities.relation import Relation
from Dtos.document import DocumentInfo
from config.config import documents_collection, annotations_collection, relations_collection
from Dal.Entities.document import Document
from bson import ObjectId



class DocumentRepository:

    def data_to_entity_helper(self, db_object) -> Document:
        result = {}
        result["id"] = str(db_object["_id"])
        result["title"] = db_object["title"]
        result["file_name"] = db_object["file_name"]
        result["date"] = db_object["date"]
        annotations: List[Annotation] = []
        for item in db_object["annotations"]:
            v = item
            v["id"] = str(item["_id"])
            v["document_id"] = str(item["document_id"])
            del v["_id"]
            annotations.append(v)
        result["annotations"] = annotations
        relations: List[Relation] =[]
        for item in db_object["relations"]:
            relations.append(Relation(id=str(item["_id"]),id_from=str(item["id_from"]), id_to=str(item["id_to"]), document_id=str(item["document_id"]), tags=item["tags"]))
        return Document(**result, relations=relations)


    def get_one_document(self, id: str) -> Optional[Document]:
        doc = documents_collection.find_one({"_id": ObjectId(id)})
        if (doc is None):
            return None
        return self.data_to_entity_helper(doc)
        

    def get_documents(self) -> List[DocumentInfo]:
        docs = documents_collection.find()
        result = []
        for item in docs:
            result.append(DocumentInfo(id=str(item["_id"]), title=item["title"],
                                        file_name=item["file_name"], date=item["date"], count_annotations=len(item["annotations"]) + len(item["relations"])))
        return result


    def add_document(self, new_document: Document) -> Optional[DocumentInfo]:
        db_data = new_document.dict()
        del db_data["id"]
        result = documents_collection.insert_one(db_data)
        if result.acknowledged:
            return DocumentInfo(id=str(result.inserted_id), title=new_document.title,
                                 file_name=new_document.file_name, date=new_document.date, count_annotations=0) 
        else:
            None

    def del_document(self, id: str) -> bool:
        result_doc = documents_collection.delete_one({"_id": ObjectId(id)})
        if(not result_doc.acknowledged or result_doc.deleted_count == 0):
            return False
        result_annot = annotations_collection.delete_many({"document_id": ObjectId(id)})
        if(not result_annot.acknowledged):
            return False
        result_relat = relations_collection.delete_many({"document_id": ObjectId(id)})
        if(not result_relat.acknowledged):
            return False
        return True
    


        


