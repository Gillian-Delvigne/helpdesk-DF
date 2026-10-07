from app.framework.mapper.abstract_mapper import AbstractMapper
from app.dtos.attachment_dto import AttachmentDTO
from app.forms.attachment_form import AttachmentForm
from app.models.attachment import Attachment
from app import os


class AttachmentMapper(AbstractMapper):

    @staticmethod
    def entity_to_dto(attachment: Attachment) -> AttachmentDTO:
        return AttachmentDTO.build_from_entity(attachment)

    @staticmethod
    def form_to_entity(form, attachment: Attachment, author_id: int, ticket_id: int, attachment_filename: str, attachment_path: str, attachment_size: int) -> Attachment:
        if isinstance(form, AttachmentForm):

                attachment.attachment_filename = attachment_filename
                attachment.attachment_path = attachment_path
                attachment.attachment_size = attachment_size
                attachment.ticket_id = ticket_id
                attachment.author_id = author_id

        return attachment