import random
from datetime import datetime, timedelta, timezone

from app import app, db
from app.framework.seed import Seedable
from app.models.category import Category
from app.models.equipment import Equipment
from app.models.priority import Priority
from app.models.ticket import Ticket
from app.models.ticket_status import TicketStatusEnum
from app.models.user import User

TICKET_TITLES = [
    "Ordinateur ne démarre plus",
    "Impossible de se connecter au VPN",
    "Écran qui clignote",
    "Demande de nouveau compte AD",
    "Imprimante bloquée avec bourrage papier",
    "Wifi coupe régulièrement",
    "Erreur lors de l'installation de Microsoft 365",
    "Scanner entrepôt hors service",
    "Mot de passe oublié",
    "Demande d'accès à un dossier partagé",
]

# Répartition volontairement inégale : plus de tickets déjà traités que de
# nouveaux, pour que la carte "par statut" ait une vraie forme.
STATUS_WEIGHTS = {
    TicketStatusEnum.NEW: 3,
    TicketStatusEnum.IN_PROGRESS: 5,
    TicketStatusEnum.BLOCKED: 2,
    TicketStatusEnum.RESOLVED: 8,
    TicketStatusEnum.CLOSED: 12,
}

TICKET_COUNT = 30
DAYS_SPREAD = 60


class TicketMockSeed(Seedable):
    order = 60

    def seed(self):
        if Ticket.query.first() is not None:
            app.logger.debug("Seed tickets: déjà des tickets en base, seed ignoré")
            return

        categories = Category.query.all()
        priorities = Priority.query.all()
        equipments = Equipment.query.all()
        clients = [u for u in User.query.all() if u.has_role("CLIENT")]
        # Triés par id (pas par nom) : la répartition de charge ne doit dépendre
        # que de COMBIEN de techniciens existent, jamais de noms codés en dur —
        # ceux-ci viennent de UserSeed (ou de n'importe quel autre seed d'équipe),
        # jamais garantis identiques d'un poste à l'autre.
        technicians = sorted(
            (u for u in User.query.all() if u.has_role("TECHNICIEN")),
            key=lambda u: u.user_id,
        )

        if not (categories and priorities and equipments and clients and technicians):
            app.logger.warning(
                "Seed tickets: données de référence manquantes "
                "(catégories/priorités/équipements/clients/techniciens) — seed reporté"
            )
            return

        statuses = list(STATUS_WEIGHTS.keys())
        status_weights = list(STATUS_WEIGHTS.values())

        # Poids décroissants selon la position : charge volontairement inégale entre
        # techniciens, quel que soit leur nombre réel en base (1, 3, ou 10).
        technician_weight_values = [
            max(1, len(technicians) - i) for i in range(len(technicians))
        ]

        # Graine fixe : mêmes données générées à chaque reseed, reproductible pour toute l'équipe.
        rng = random.Random(42)
        now = datetime.now(timezone.utc)

        for _ in range(TICKET_COUNT):
            category = rng.choice(categories)
            priority = rng.choice(priorities)
            equipment = rng.choice(equipments)
            author = rng.choice(clients)
            status = rng.choices(statuses, weights=status_weights, k=1)[0]

            technician = None
            if status != TicketStatusEnum.NEW:
                technician = rng.choices(
                    technicians, weights=technician_weight_values, k=1
                )[0]

            created_at = now - timedelta(
                days=rng.randint(0, DAYS_SPREAD), hours=rng.randint(0, 23)
            )
            due_date = (created_at + timedelta(hours=priority.delay_hours)).date()

            ticket = Ticket(
                title=rng.choice(TICKET_TITLES),
                description="Ticket de démonstration généré pour le tableau de bord.",
                status=status,
                due_date=due_date,
                author_id=author.user_id,
                technician_id=technician.user_id if technician else None,
                category_id=category.category_id,
                priority_id=priority.priority_id,
                equipment_id=equipment.equipment_id,
            )
            # Backdater la création : sans ça, server_default poserait "maintenant"
            # pour tous les tickets, et la carte "évolution dans le temps" serait plate.
            ticket.created_at = created_at
            db.session.add(ticket)

        app.logger.debug(f"Seed de {TICKET_COUNT} tickets de démonstration")
        db.session.commit()
