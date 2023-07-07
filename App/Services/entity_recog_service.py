from typing import List, Optional
from Dtos.annotation import Annotation
from Dal.Entities.annotation import Annotation as AnnotationEntity
from Dal.Repositories.annotation_repo import AnnotationRepository
from Dal.Repositories.document_repo import DocumentRepository
from Services.parsers import DocumentParser
from Services.service import Service, get_file_content
import spacy


class EntityRecognitionService(Service):

    def __init__(self, annotation_repo: AnnotationRepository, doc_parser: DocumentParser) -> None:
        self.annotation_repository = annotation_repo
        self.nlp = spacy.load('en_core_web_sm')
        self.document_parser = doc_parser

    def run_spacy_ner(self, id: str) -> Optional[List[Annotation]]:
        if self.validate_id(id) == False:
            return None
        text = get_file_content(id)
        doc = self.nlp(text)
        annotations = []
        for ent in doc.ents:
            annotations.append(AnnotationEntity(tags=[ent.label_], comments=[],
                                                location={"start": ent.start_char, "end": ent.end_char},
                                                text=ent.text, document_id=id))
        all_entity_annotation_in_doc =  self.annotation_repository.add_annotation_list(annotations)
        
        return self.document_parser.db_to_response_annotations(all_entity_annotation_in_doc)
        


        