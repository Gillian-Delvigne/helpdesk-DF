import random
from datetime import datetime, timedelta, timezone

from app import app, db
from app.framework.seed import Seedable
from app.models.ticket import Ticket
from app.models.ticket_status import TicketStatusEnum
from app.models.ticket_status_history import TicketStatusHistory

# Statuts pour lesquels on trace une "date de résolution" simulée.
RESOLVED_LIKE = [TicketStatusEnum.RESOLVED, TicketStatusEnum.CLOSED]


class TicketStatusHistorySeed(Seedable):
    order = 70

    def seed(self):
        if TicketStatusHistory.query.first() is not None:
            app.logger.debug("Seed historique de statuts: déjà présent, seed ignoré")
            return

        tickets = Ticket.query.filter(Ticket.status.in_(RESOLVED_LIKE)).all()

        if not tickets:
            app.logger.debug(
                "Seed historique de statuts: aucun ticket résolu/clos à tracer"
            )
            return

        # Graine différente des autres seeds pour ne pas corréler les tirages entre eux.
        rng = random.Random(43)

        for ticket in tickets:
            # Simule une résolution tantôt avant, tantôt après l'échéance (due_date),
            # pour que le taux de respect du SLA calculé par le dashboard ne soit ni 0 % ni 100 %.
            due_datetime = datetime.combine(
                ticket.due_date, datetime.min.time(), tzinfo=timezone.utc
            )
            offset_hours = rng.randint(-48, 48)  # négatif = en avance, positif = en retard
            resolved_at = due_datetime + timedelta(hours=offset_hours)

            history = TicketStatusHistory(
                ticket_id=ticket.ticket_id,
                user_id=ticket.technician_id or ticket.author_id,
                old_status=TicketStatusEnum.IN_PROGRESS.value,
                new_status=ticket.status.value,
            )
            history.created_at = resolved_at
            db.session.add(history)

        app.logger.debug(f"Seed historique de statuts pour {len(tickets)} tickets")
        db.session.commit()
