from typing import Optional, List
from Dtos.update_annotation import UpdateAnnotation
from config.config import documents_collection, annotations_collection, relations_collection
from Dal.Entities.annotation import Annotation
from bson import ObjectId



class AnnotationRepository:

    """def get_annotations(self) -> List[Annotation]:
        data = annotations_collection.find()
        return [Annotation(**item) for item in data]"""
    
    def add_annotation(self, new_annotation: Annotation) -> Optional[str]:
        db_data = new_annotation.dict()
        db_data["document_id"] = ObjectId(db_data["document_id"])
        del db_data["id"]
        result = annotations_collection.insert_one(db_data)
        if not result.acknowledged:
            return None
        db_data["_id"] = result.inserted_id
        query_update = {"$push": {"annotations": db_data}}
        documents_collection.update_one({"_id": db_data["document_id"]}, query_update)
        return str(result.inserted_id)
    
    def add_annotation_list(self, annotations: List[Annotation]) -> List[Annotation]:
        if len(annotations) == 0:
            print("asd")
            return []
        objts = []
        for item in annotations:
            ann = annotations_collection.find_one({"location": {"start": item.location.start, "end": item.location.end}, "document_id": ObjectId(annotations[0].document_id)})
            if ann is None:
                o = item.dict()
                o["document_id"] = ObjectId(o["document_id"])
                del o["id"]
                objts.append(o)
        if len(objts) == 0:
            print("nullameret")
            return []
        result = annotations_collection.insert_many(objts)
        if not result.acknowledged:
            print("nemacknoledged")
            return []
        annotationIterator = annotations_collection.find({"document_id": ObjectId(annotations[0].document_id)})
        addedAnnotationsWithId = []
        for i in annotationIterator:
            if i["_id"] in result.inserted_ids:
                addedAnnotationsWithId.append(i)
        documents_collection.update_one({"_id": ObjectId(annotations[0].document_id)}, {"$push": {"annotations": {"$each": [a for a in addedAnnotationsWithId]}}})
        returnResult = []
        for i in addedAnnotationsWithId:
            returnResult.append(Annotation(id=str(i["_id"]), tags=i["tags"], comments=i["comments"],
                                      document_id=str(i["document_id"]), location={"start": i["location"]["start"], "end": i["location"]["end"]}, text=i["text"]))
        
        return returnResult

        
        
        
    def get_one_annotation(self, id: str) -> Optional[Annotation]:
        id = ObjectId(id)
        obj = annotations_collection.find_one({"_id": id})
        if obj is None:
            return None
        obj["id"] = str(obj["_id"])
        obj["document_id"] = str(obj["document_id"])
        del obj["_id"]
        return Annotation(**obj)



    def del_annotation(self, id: str) -> bool:
        deleted_annotation = annotations_collection.find_one_and_delete({"_id": ObjectId(id)})
        if(deleted_annotation is None):
            return False
        
        deleted_relations = relations_collection.delete_many({
                                    "$or": [
                                        {"id_from": ObjectId(id)},
                                        {"id_to": ObjectId(id)}
                                    ]
                                })
        
        query = {"_id": deleted_annotation["document_id"]}
        update = {
            "$pull": {
                "annotations": deleted_annotation,
                "relations": {
                    "$or": [
                        {"id_from": ObjectId(id)},
                        {"id_to": ObjectId(id)}
                    ]
                }
            }
        }
        res_updt = documents_collection.update_one(query, update)
        
        if(not res_updt.acknowledged):
            return False
        return True
    
    def update_annotation(self, id: str, changes: UpdateAnnotation) -> bool:
        result = annotations_collection.update_one({"_id": ObjectId(id)},
                                    {"$set": {"comments": changes.comments, "tags": changes.tags}})
        
        if(not result.acknowledged):
            return False
        annotation = annotations_collection.find_one({"_id": ObjectId(id)})
        query = {"_id": annotation["document_id"], "annotations._id": annotation["_id"]}
        update = {"$set": {"annotations.$": annotation}}
        res = documents_collection.update_one(query, update)
        if(not res.acknowledged):
            return False
        return True
        
    
