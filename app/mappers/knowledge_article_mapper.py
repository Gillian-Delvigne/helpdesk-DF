from app.framework.mapper import AbstractMapper
from app.models.knowledge_article import KnowledgeArticle
from app.dtos.knowledge_article_dto import KnowledgeArticleDTO

class EquipmentMapper(AbstractMapper):

    @staticmethod
    def entity_to_dto(entity: KnowledgeArticle) -> KnowledgeArticleDTO:
        return KnowledgeArticleDTO.build_from_entity(entity)
        