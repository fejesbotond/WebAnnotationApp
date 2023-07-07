from Dal.Repositories.annotation_repo import AnnotationRepository
from Dal.Repositories.document_repo import DocumentRepository
from Dal.Repositories.relation_repo import RelationRepository
from Dal.Repositories.tags_repo import TagsRepository
from Services.Annotation.annotation_service import AnnotationService
from Services.Document.document_service import DocumentService
from Services.Relation.relation_service import RelationService
from Services.Tags.tags_service import TagsService
from Services.entity_recog_service import EntityRecognitionService
from Services.parsers import DocumentParser, AnnotationParser, RelationParser

def get_document_service() -> DocumentService:
    return DocumentService(DocumentRepository(), DocumentParser(AnnotationParser(), RelationParser()))

def get_annotation_service() -> AnnotationService:
    return AnnotationService(AnnotationRepository(), DocumentRepository(), TagsRepository(), AnnotationParser())

def get_tags_service() -> TagsService:
    return TagsService(TagsRepository())

def get_relation_service() -> RelationService:
    return RelationService(RelationRepository(), DocumentRepository(), TagsRepository(), AnnotationRepository(), RelationParser())

def get_entity_recognition_service() -> EntityRecognitionService:
    return EntityRecognitionService(AnnotationRepository(), DocumentParser(AnnotationParser(), RelationParser()))