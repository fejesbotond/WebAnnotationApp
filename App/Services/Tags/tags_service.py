from typing import List
from Dal.Repositories.tags_repo import TagsRepository
from Dtos.tags import Tags
from Services.service import Service


class TagsService(Service):
    def __init__(self, repository: TagsRepository):
        self.repository = repository

    def get_entity_tags(self) -> List[str]:
        db_tags = self.repository.get_tags()
        return db_tags
    
    def get_relation_tags(self) -> List[str]:
        db_tags = self.repository.get_relation_tags()
        return db_tags