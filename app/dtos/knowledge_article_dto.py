from app.framework.dto import AbstractDTO
from app.dtos.user_dto import UserDTO
from app.dtos.category_dto import CategoryDTO
from app.models.knowledge_article import KnowledgeArticle

class KnowledgeArticleDTO(AbstractDTO):

    def __init__(self) -> None:
        super().__init__()
        self.article_id = None
        self.title = None
        self.content = None
        self.category: list[CategoryDTO] = []
        self.author: list[UserDTO] = []


    @staticmethod
    def build_from_entity(entity: KnowledgeArticle) -> "KnowledgeArticleDTO":
        knowledge_article_dto = KnowledgeArticleDTO()

        knowledge_article_dto.article_id = entity.article_id
        knowledge_article_dto.title = entity.title
        knowledge_article_dto.content = entity.content

        knowledge_article_dto.category = [CategoryDTO.build_from_entity(article_category) 
                                            for article_category in entity.category]

        knowledge_article_dto.author = [UserDTO.build_from_entity(article_author) for article_author in entity.author]

        return knowledge_article_dto


    def get_json_parsable(self):
        data = dict(self.__dict__)
        data['category'] = [category.get_json_parsable() for category in self.category]
        data['author'] = [author.get_json_parsable() for author in self.author]
        return data