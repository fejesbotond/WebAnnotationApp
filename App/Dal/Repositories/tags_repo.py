from typing import List
from config.config import tags_annotations_collection, tags_relations_collection

class TagsRepository:

    def get_tags(self) -> List[str]:
        res = []
        entityTagsP = tags_annotations_collection.find()
        for item in entityTagsP:
            res.append(item["value"])
        return res
    
    def get_relation_tags(self) -> List[str]:
        res = []
        relation_tags = tags_relations_collection.find()
        for item in relation_tags:
            res.append(item["value"])
        return res
