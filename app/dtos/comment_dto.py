from app.framework.dto import AbstractDTO
from app.models.comment import Comment

class CommentDTO(AbstractDTO):

    def __init__(self):
        super().__init__()
        self.comment_id = None
        self.comment_content = None
        self.author_id = None
        self.ticket_id = None

    @staticmethod
    def build_from_entity(entity) -> "CommentDTO":
        comment_dto = CommentDTO()

        if isinstance(entity, Comment):
            comment_dto.comment_id = entity.comment_id
            comment_dto.comment_content = entity.comment_content
            comment_dto.author_id = entity.author_id
            comment_dto.ticket_id = entity.ticket_id
            comment_dto.created_at = entity.created_at
            comment_dto.updated_at = entity.updated_at

        return comment_dto

    def get_json_parsable(self):
        return {
            "comment_id": self.comment_id,
            "comment_content": self.comment_content,
            "author_id": self.author_id,
            "ticket_id": self.ticket_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        