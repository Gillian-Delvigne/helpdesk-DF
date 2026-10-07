from app.framework.dto.abstract_dto import AbstractDTO
from app.models.ticket_status_history import TicketStatusHistory

class TicketStatusHistoryDTO(AbstractDTO):
    def __init__(self):
        super().__init__()
        self.history_id = None
        self.ticket_id = None
        self.user_id = None
        self.old_status = None
        self.new_status = None

    @staticmethod
    def build_from_entity(entity):
        ticket_status_history_dto = TicketStatusHistoryDTO()

        if isinstance(entity, TicketStatusHistory):
            ticket_status_history_dto.history_id = entity.history_id
            ticket_status_history_dto.ticket_id = entity.ticket_id
            ticket_status_history_dto.user_id = entity.user_id
            ticket_status_history_dto.old_status = entity.old_status
            ticket_status_history_dto.new_status = entity.new_status
            ticket_status_history_dto.created_at = entity.created_at
            ticket_status_history_dto.updated_at = entity.updated_at

        return ticket_status_history_dto

    def get_json_parsable(self):
        return {
            "history_id": self.history_id,
            "ticket_id": self.ticket_id,
            "user_id": self.user_id,
            "old_status": self.old_status.value if self.old_status else None,
            "new_status": self.new_status.value if self.new_status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
            }