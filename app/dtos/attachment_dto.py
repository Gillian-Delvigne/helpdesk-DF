from app.framework.dto import AbstractDTO
from app.models.attachment import Attachment


class AttachmentDTO(AbstractDTO):

    def __init__(self):
        super().__init__()
        self.attachment_id = None
        self.attachment_filename = None
        self.attachment_path = None
        self.attachment_size = None
        self.ticket_id = None
        self.author_id = None

    @staticmethod
    def build_from_entity(entity) -> "AttachmentDTO":
        attachment_dto = AttachmentDTO()

        if isinstance(entity, Attachment):
            attachment_dto.attachment_id = entity.attachment_id
            attachment_dto.attachment_filename = entity.attachment_filename
            attachment_dto.attachment_path = entity.attachment_path
            attachment_dto.attachment_size = entity.attachment_size
            attachment_dto.ticket_id = entity.ticket_id
            attachment_dto.author_id = entity.author_id
            attachment_dto.created_at = entity.created_at
            attachment_dto.updated_at = entity.updated_at

        return attachment_dto

    def get_json_parsable(self):
        return {
            "attachment_id": self.attachment_id,
            "attachment_filename": self.attachment_filename,
            "attachment_path": self.attachment_path,
            "attachment_size": self.attachment_size,
            "ticket_id": self.ticket_id,
            "author_id": self.author_id,
            "created_at": self.created_at.isoformat()
                if self.created_at else None,
            "updated_at": self.updated_at.isoformat()
                if self.updated_at else None
        }