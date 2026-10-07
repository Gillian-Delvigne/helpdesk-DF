from app.models.ticket_status import TicketStatusEnum
from app.framework.decorators.injectable import injectable
from flask import flash, redirect, url_for
from app.models.priority import Priority
from datetime import timedelta, datetime
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from app.dtos.ticket_dto import TicketDTO
from app.forms.tickets.ticket_form import TicketForm
from app.mappers.ticket_mapper import TicketMapper
from app.models.ticket import Ticket
from app.framework.service import AbstractService
from app.framework.decorators.inject import inject
from .auth_service import AbstractAuthService

@injectable
class TicketService(AbstractService):
    @inject
    def insert(self, form: TicketForm, auth_service: AbstractAuthService) -> TicketDTO | None:
        try:
            ticket = Ticket()
            TicketMapper.form_to_entity(form, ticket)

            # Set current user as author
            current_user = auth_service.get_current_user()
            if current_user is None:
                flash("Vous devez être connecté pour créer un ticket", "warning")
                app.logger.error("Utilisateur non connecté lors de la création d'un ticket")
                return None

            ticket.author_id = current_user.user_id
            
            # Set status to "New" by default
            ticket.status = TicketStatusEnum.NEW

            # Compute due date (now + (priority delay in hours))
            delay = Priority.query.get(ticket.priority_id).delay_hours
            ticket.due_date = datetime.now() + timedelta(hours=delay)

            db.session.add(ticket)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la création du ticket: {e}")
            return None
        else:
            return TicketMapper.entity_to_dto(ticket)

    # Used for technicians to see ALL tickets
    # TODO: Add order by date (newest to oldest)
    def find_all(self):
        tickets = Ticket.query.all()
        return [TicketMapper.entity_to_dto(t) for t in tickets]

    # Used for clients to see all tickets they created
    # TODO: Add order by date (newest to oldest)
    def find_all_by(self, **kwargs):
        tickets = Ticket.query.filter_by(author_id=kwargs["author_id"]).all()
        return [TicketMapper.entity_to_dto(t) for t in tickets]

    def find_one(self, entity_id: int):
        ticket = Ticket.query.get(entity_id)
        if ticket is None:
            return None
        return TicketMapper.entity_to_dto(ticket)

    def find_one_by(self, **kwargs):
        pass

    def find_one_entity(self, entity_id: int):
        ticket = Ticket.query.get(entity_id)
        if ticket is None:
            return None
        return ticket

    def update(self, entity_id: int, data):
        pass

    def delete(self, entity_id: int):
        pass

    def update_ticket_status(self, ticket_id: int, new_status: str, current_user_id: int):

        try: 
            ticket = self.find_one_entity(ticket_id)
            if not ticket:
                return None

            old_status = ticket.status

            if old_status.value == new_status:
                return True

            if new_status not in TicketStatusEnum.values():
                return None
                
            ticket.status = new_status

            history_data = {
                "ticket_id": ticket_id,
                "user_id": current_user_id,
                "old_status": old_status,
                "new_status": new_status,            
            }

            from app.services.ticket_status_history_service import TicketStatusHistoryService
            history_service = TicketStatusHistoryService()
            history_service.insert(history_data)

            db.session.commit()

            return TicketMapper.entity_to_dto(ticket)    

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error | change status ticket error : {e}")
            return None