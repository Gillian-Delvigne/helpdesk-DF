from argon2 import PasswordHasher
from sqlalchemy import or_

from app import app, db
from app.framework.seed import Seedable
from app.models.user import User
from app.models.role import Role
from app.seed import USERS

hasher = PasswordHasher()


class UserSeed(Seedable):
    order = 20

    def seed(self):
        for (
            name,
            email,
            password,
            firstname,
            lastname,
            _,
            _,
            roles,
        ) in USERS:
            # Vérifie le nom ET l'email : un simple filtre sur le nom laissait
            # passer un email déjà pris par un autre user (ex. renommé depuis),
            # provoquant un UniqueViolation qui plantait tous les seeders suivants.
            if User.query.filter(or_(User.name == name, User.email == email)).first() is not None:
                app.logger.debug(f"Seed user {name}: déjà présent (nom ou email)")
                continue

            user = User(
                name=name,
                email=email,
                password=hasher.hash(password),
                firstname=firstname,
                lastname=lastname,
            )

            db.session.add(user)

            for role_name in roles:
                role = Role.query.filter_by(name=role_name).first()
                user.add_role(role)

            app.logger.debug(f"Seed user {name}")
        db.session.commit()
