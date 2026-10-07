from app import db, app
from app.framework.service.abstract_service import AbstractService
from app.framework.decorators.injectable import injectable
from app.mappers.ticket_status_history_mapper import TicketStatusHistoryMapper
from app.models.ticket_status_history import TicketStatusHistory

@injectable
class TicketStatusHistoryService(AbstractService):

    def find_all(self):
        """Tous les historiques de status."""
        try:
            status_histories = TicketStatusHistory.query.all()

            return [TicketStatusHistoryMapper.entity_to_dto(status_history) for status_history in status_histories]

        except Exception as e:
            app.logger.error(f"Error | ticket status history find all impossible: {e}")
            return None

    def find_all_by(self, **kwargs):
        """Tous les historiques de status selon un critère"""

        try:
            status_histories = (
                TicketStatusHistory.query
                .filter_by(**kwargs)
                .order_by(TicketStatusHistory.created_at.desc())
                .all()
                )

            return [TicketStatusHistoryMapper.entity_to_dto(status_history) for status_history in status_histories]        

        except Exception as e:
            app.logger.error(f"Error | ticket status history find all by impossible: {e}")
            return []        

    def find_one_entity(self, entity_id: int):
        """Un historique par son Id ou None."""

        try:
            status_history = db.session.get(TicketStatusHistory, entity_id)

            if status_history is None:
                return None

            return status_history

        except Exception as e:
            app.logger.error(f"Error | ticket status history find one entity impossible: {e}")
            return None
    
    def find_one(self, entity_id: int):
        """Un DTO de l'historique par son Id, ou None."""

        try:
            status_history = db.session.get(TicketStatusHistory, entity_id)

            if status_history is None:
                return None

            return TicketStatusHistoryMapper.entity_to_dto(status_history)

        except Exception as e:
            app.logger.error(f"Error | ticket status history find one impossible: {e}")
            return None
        
    def find_one_by(self, **kwargs):
        """Un historique sur base de critère(s)"""

        try:
            status_history = TicketStatusHistory.query.filter_by(**kwargs).one_or_none()

            if status_history is None:
                return None

            return TicketStatusHistoryMapper.entity_to_dto(status_history)

        except Exception as e:
            app.logger.error(f"Error | ticket status history find one by impossible: {e}")
            return None
        
    def insert(self, data: dict):
        """Crée un historique de status"""
        try : 
            new_history = TicketStatusHistory()

            new_history.ticket_id = data.get("ticket_id")
            new_history.user_id = data.get("user_id")
            new_history.old_status = data.get("old_status")
            new_history.new_status = data.get("new_status")

            db.session.add(new_history)
            db.session.commit()

            return TicketStatusHistoryMapper.entity_to_dto(new_history)

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error | ticket status history insert impossible: {e}")
            return None
            

    def update(self, entity_id: int, data: dict):
        """Met à jour un historique de status existant."""
        try:
            status_history = db.session.get(TicketStatusHistory, entity_id)

            if status_history is None:
                return None

            status_history.ticket_id = data.get("ticket_id", status_history.ticket_id)
            status_history.user_id = data.get("user_id", status_history.user_id)
            status_history.old_status = data.get("old_status", status_history.old_status)
            status_history.new_status = data.get("new_status", status_history.new_status)

            db.session.commit()

            return TicketStatusHistoryMapper.entity_to_dto(status_history)
            

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error | ticket status history update impossible: {e}")
            return None

    def delete(self, entity_id: int):
        """Bloque la suppression d'un historique pour protéger l'intégrité des données de suivis"""
        app.logger.warning(f"Tentative interdite de suppression de l'historique avec l'ID {entity_id}")
        raise NotImplementedError("Un historique de status ne peut pas être supprimé.")