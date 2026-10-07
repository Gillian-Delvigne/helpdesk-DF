from datetime import date

from app import app, db
from app.framework.seed import Seedable
from app.models.equipment import Equipment
from app.models.site import Site

# (nom, type, date d'achat, numéro de série)
EQUIPMENTS = [
    ("PC-Bureau-01", "Laptop", date(2023, 3, 14), "EQ-0001"),
    ("PC-Bureau-02", "Laptop", date(2023, 3, 14), "EQ-0002"),
    ("Ecran-Dell-24", "Monitor", date(2022, 11, 2), "EQ-0003"),
    ("Imprimante-Etiquettes-01", "Printer", date(2021, 6, 19), "EQ-0004"),
    ("Scanner-Entrepot-01", "Scanner", date(2020, 9, 30), "EQ-0005"),
    ("Switch-Reseau-A1", "Network", date(2021, 1, 10), "EQ-0006"),
    ("Routeur-VPN-01", "Network", date(2022, 5, 5), "EQ-0007"),
    ("PC-Portable-Direction", "Laptop", date(2024, 1, 20), "EQ-0008"),
]


class EquipmentSeed(Seedable):
    order = 50

    def seed(self):
        site = Site.query.filter_by(name="Technobel").first()
        if site is None:
            app.logger.warning("Seed equipment: site 'Technobel' absent, seed reporté")
            return

        for name, type_, purchase_date, serial in EQUIPMENTS:
            if Equipment.query.filter_by(name=name).first() is not None:
                continue

            app.logger.debug(f"Seed equipment {name}")
            db.session.add(
                Equipment(
                    name=name,
                    type=type_,
                    purchase_date=purchase_date,
                    serial=serial,
                    site_id=site.site_id,
                )
            )

        db.session.commit()
