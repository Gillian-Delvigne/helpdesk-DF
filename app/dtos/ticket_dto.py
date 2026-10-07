from app.framework.dto import AbstractDTO
from app.dtos.category_dto import CategoryDTO
from app.dtos.priority_dto import PriorityDTO
from app.models.ticket import Ticket
from app.dtos.comment_dto import CommentDTO
from app.dtos.attachment_dto import AttachmentDTO
from app.dtos.ticket_status_history_dto import TicketStatusHistoryDTO


class TicketDTO(AbstractDTO):
    
    def __init__(self):
        super().__init__()
        self.ticket_id = None
        self.ticket_title = None
        self.ticket_description = None
        self.ticket_status = None
        self.ticket_due_date = None
        self.ticket_author_id = None
        self.ticket_technician_id = None
        self.ticket_category_id = None
        self.ticket_priority_id = None
        self.ticket_category = None
        self.ticket_priority = None
        self.ticket_comments = []
        self.ticket_attachments = []
        self.ticket_status_histories = []

    @staticmethod
    def build_from_entity(ticket: Ticket) -> "TicketDTO":
        ticket_dto = TicketDTO()

        ticket_dto.ticket_id = ticket.ticket_id
        ticket_dto.ticket_title = ticket.title
        ticket_dto.ticket_description = ticket.description
        ticket_dto.ticket_status = ticket.status
        ticket_dto.ticket_due_date = ticket.due_date
        ticket_dto.ticket_author_id = ticket.author_id
        ticket_dto.ticket_technician_id = ticket.technician_id
        ticket_dto.ticket_category_id = ticket.category_id
        ticket_dto.ticket_priority_id = ticket.priority_id
        
        ticket_dto.ticket_category = (
            CategoryDTO.build_from_entity(ticket.category) if ticket.category else None
        )
        ticket_dto.ticket_priority = (
            PriorityDTO.build_from_entity(ticket.priority) if ticket.priority else None
        )
        
        ticket_dto.ticket_comments = [
            CommentDTO.build_from_entity(comment) for comment in ticket.comments
        ] if ticket.comments else []

        ticket_dto.ticket_attachments = [
            AttachmentDTO.build_from_entity(attachment) for attachment in ticket.attachments
        ] if ticket.attachments else []

        ticket_dto.ticket_status_histories = [
            TicketStatusHistoryDTO.build_from_entity(sh) for sh in ticket.status_histories
        ] if ticket.status_histories else []

        return ticket_dto
    
    def get_json_parsable(self):
        data = dict(self.__dict__)
        
        if self.ticket_due_date:
            data['ticket_due_date'] = self.ticket_due_date.isoformat()
            
        if self.ticket_category:
            data['ticket_category'] = self.ticket_category.get_json_parsable()

        if self.ticket_priority:
            data['ticket_priority'] = self.ticket_priority.get_json_parsable()

        if self.ticket_status and hasattr(self.ticket_status, 'value'):
            data['ticket_status'] = self.ticket_status.value

        data['ticket_comments'] = [comment.get_json_parsable() for comment in self.ticket_comments]
        data['ticket_attachments'] = [attachment.get_json_parsable() for attachment in self.ticket_attachments]
        data['ticket_status_histories'] = [sh.get_json_parsable() for sh in self.ticket_status_histories]
        
        return data