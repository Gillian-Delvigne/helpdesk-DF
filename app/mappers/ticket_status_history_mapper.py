from app.framework.mapper.abstract_mapper import AbstractMapper
from app.dtos.ticket_status_history_dto import TicketStatusHistoryDTO
from app.models.ticket_status_history import TicketStatusHistory


class TicketStatusHistoryMapper(AbstractMapper):
    @staticmethod
    def entity_to_dto(ticketstatushistory: TicketStatusHistory) -> TicketStatusHistoryDTO:
        return TicketStatusHistoryDTO.build_from_entity(ticketstatushistory)

    @staticmethod
    def form_to_entity(form, entity):
        raise NotImplementedError("Cette méthode n'est pas utilisée pour l'historique des status.")


