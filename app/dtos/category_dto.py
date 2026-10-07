from app.framework.dto import AbstractDTO
from app.models.category import Category


class CategoryDTO(AbstractDTO):

    def __init__(self):
        super().__init__()
        self.category_id = None
        self.category_name = None
        self.category_description = None
        self.tickets_list = []
        self.knowledge_articles = []

    @staticmethod
    def build_from_entity(category: Category, include_tickets: bool = False) -> "CategoryDTO":

        category_dto = CategoryDTO()

        category_dto.category_id = category.category_id
        category_dto.category_name = category.name
        category_dto.category_description = category.description

        from app.dtos.ticket_dto import TicketDTO
        from app.dtos.knowledge_article_dto import KnowledgeArticleDTO

        if include_tickets and category.ticket:
            category_dto.tickets_list = [TicketDTO.build_from_entity(ticket)
                                     for ticket in category.tickets]
        else:
            category_dto.tickets_list = []

        category_dto.knowledge_articles = [KnowledgeArticleDTO.build_from_entity(article)
                                           for article in category.knowledge_articles]

        return category_dto
    
    def get_json_parsable(self):
        data = dict(self.__dict__)
        data['tickets_list'] = [ticket.get_json_parsable() for ticket in self.tickets_list]
        data['knowledge_articles'] = [article.get_json_parsable() for article in self.knowledge_articles]
        return data