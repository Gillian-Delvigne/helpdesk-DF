from app import app, db
from app.framework.seed.seedable import Seedable
from app.models.user import User
from app.models.equipment import Equipment
from app.models.site import Site
from app.seed import SITES

class SiteSeed(Seedable):
    order = 40

    def seed(self):
        for sitename, address, city, user_names, equipment_names in SITES:
            if Site.query.filter_by(name=sitename).first():
                app.logger.debug(f"Seed site {sitename}: déjà présent")
                continue
            
            site = Site(
                name=sitename,
                address=address,
                city=city)

            db.session.add(site)

            for user_name in user_names:
                user = User.query.filter_by(name=user_name).first()

                if user is None:
                    app.logger.warning(f"Seed site {sitename}: user {user_name} absent")
                    continue

                site.add_user(user)

            for equipment_name in equipment_names:
                equipment = Equipment.query.filter_by(name=equipment_name).first()

                if equipment is None:
                    app.logger.warning(f"Seed site {sitename}: equipment {equipment_name} absent")
                    continue

                site.add_equipment(equipment)

            app.logger.debug(f"Seed site {sitename}")

        db.session.commit()