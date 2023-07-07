from typing import List, Optional
from Dal.Entities.relation import Relation
from bson import ObjectId

from config.config import relations_collection, documents_collection



class RelationRepository:

    def add_relation(self, relation_item: Relation) -> Optional[str]:
        db_data = relation_item.dict()
        db_data["document_id"] = ObjectId(db_data["document_id"])
        db_data["id_from"] = ObjectId(db_data["id_from"])
        db_data["id_to"] = ObjectId(db_data["id_to"])
        del db_data["id"]
        result = relations_collection.insert_one(db_data)
        if not result.acknowledged:
            return None
        db_data["_id"] = result.inserted_id
        query_update = {"$push": {"relations": db_data}}
        documents_collection.update_one({"_id": db_data["document_id"]}, query_update)
        return str(result.inserted_id)

    def del_relation(self, id: str) -> bool:
        deleted_relation = relations_collection.find_one_and_delete({"_id": ObjectId(id)})
        if(deleted_relation is None):
            return False
        res_updt = documents_collection.update_one({"_id": deleted_relation["document_id"]},
                            {"$pull": {"relations": deleted_relation}})
        
        if(not res_updt.acknowledged):
            return False
        return True

    def update_relation(self, id: str, tag: str) -> bool:
        result = relations_collection.update_one({"_id": ObjectId(id)},
                                    {"$set": {"tags": [tag]}})
        
        if(not result.acknowledged):
            return False
        #relation = relations_collection.find_one({"_id": ObjectId(id)})
        query = {"relations._id": ObjectId(id)}
        update = {"$set": {"relations.$.tags": [tag]}}
        res = documents_collection.update_one(query, update)
        if(not res.acknowledged):
            return False
        return True
  
