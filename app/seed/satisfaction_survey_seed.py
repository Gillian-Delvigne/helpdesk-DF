import random

from app import app, db
from app.framework.seed import Seedable
from app.models.satisfaction_survey import SatisfactionSurvey
from app.models.ticket import Ticket
from app.models.ticket_status import TicketStatusEnum

COMMENTS_BY_RATING = {
    5: "Problème résolu rapidement, merci !",
    4: "Bonne prise en charge.",
    3: "Résolu, mais ça a pris un peu de temps.",
    2: "Plusieurs échanges nécessaires avant la résolution.",
    1: "Pas satisfait du délai de traitement.",
}


class SatisfactionSurveySeed(Seedable):
    order = 80

    def seed(self):
        if SatisfactionSurvey.query.first() is not None:
            app.logger.debug("Seed enquêtes de satisfaction: déjà présentes, seed ignoré")
            return

        closed_tickets = Ticket.query.filter_by(status=TicketStatusEnum.CLOSED).all()

        if not closed_tickets:
            app.logger.debug("Seed enquêtes de satisfaction: aucun ticket clos")
            return

        rng = random.Random(44)

        for ticket in closed_tickets:
            # Tout le monde ne répond pas à l'enquête : ~70 % de taux de réponse simulé.
            if rng.random() > 0.7:
                continue

            rating = rng.choices([5, 4, 3, 2, 1], weights=[4, 3, 2, 1, 1], k=1)[0]

            db.session.add(
                SatisfactionSurvey(
                    ticket_id=ticket.ticket_id,
                    client_id=ticket.author_id,
                    rating=rating,
                    comment=COMMENTS_BY_RATING[rating],
                )
            )

        db.session.commit()
        app.logger.debug("Seed enquêtes de satisfaction terminé")
