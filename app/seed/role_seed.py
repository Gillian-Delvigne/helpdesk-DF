from app import app, db
from app.framework.seed.seedable import Seedable
from app.models.role import Role
from app.seed import ROLES


class RoleSeed(Seedable):
    order = 10

    def seed(self):
        for name in ROLES:
            if Role.query.filter_by(name=name).first() is not None:
                app.logger.debug(f"Seed Role {name} déjà présent")
                continue
            app.logger.debug(f"Seed role {name}")
            db.session.add(Role(name=name))
        db.session.commit()
