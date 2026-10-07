from argon2 import PasswordHasher
from sqlalchemy.exc import SQLAlchemyError

from app import app, db
from app.framework.decorators.injectable import injectable
from app.framework.injector import Scope
from app.framework.service.abstract_service import AbstractService
from app.dtos.user_dto import UserDTO
from app.forms.users.user_register_form import UserRegisterForm
from app.models.role import Role
from app.models.user import User
from app.mappers.user_mapper import UserMapper
from app.forms.users.user_login_form import UserLoginForm


@injectable(scope=Scope.SCOPED)
class UserService(AbstractService):
    def __init__(self):
        self.__hasher = PasswordHasher()

    def find_all(self, active=True) -> list[UserDTO]:
        try:
            if not active:
                users = User.query.order_by(User.user_id).all()
            else:
                users = User.query.filter_by(active).order_by(User.user_id).all()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la sélection de tous les utilisateurs: {e}"
            )
            return []
        else:
            return [UserMapper.entity_to_dto(user) for user in users]

    def find_one_entity(self, user_id: int) -> User | None:
        try:
            return db.session.get(User, user_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'utilisateur, id {user_id}: {e}"
            )
            return None

    def find_one(self, user_id: int) -> UserDTO | None:
        try:
            user = db.session.get(User, user_id)
            return UserMapper.entity_to_dto(user) if user is not None else None
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'utilisateur (DTO), id {user_id}: {e}"
            )
            return None

    def find_one_by(self, **kwargs) -> UserDTO | None:
        try:
            user = User.query.filter_by(**kwargs).first()
            return UserMapper.entity_to_dto(user) if user is not None else None
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'utilisateur (DTO) avec {[f'{k} = {v}' for k, v in kwargs.items()]} : {e}"
            )
            return None

    def find_one_entity_by(self, **kwargs) -> User | None:
        try:
            user = User.query.filter_by(**kwargs).first()
            return user if user is not None else None
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'utilisateur avec {[f'{k} = {v}' for k, v in kwargs.items()]} : {e}"
            )
            return None

    def find_entities_by_ids(self, ids: list[int]) -> list[User]:
        try:
            users = (
                User.query.filter_by(active=True).filter(User.user_id.in_(ids)).all()
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération des utilisateurs portant les id {ids} : {e}"
            )
            return []
        else:
            return users

    def insert(self, form: UserRegisterForm) -> UserDTO | None:
        try:
            user = User()
            UserMapper.form_to_entity(form, user)
            user.password = self.__hasher.hash(user.password)
            role = Role.query.filter_by(name="CLIENT").first()
            if role is not None:
                user.add_role(role)
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            return None
        else:
            return UserMapper.entity_to_dto(user)

    def update(self, user_id: int, data) -> UserDTO | None:
        try:
            user = self.find_one_entity(user_id)
            if user is None:
                return None
            UserMapper.form_to_entity(data, user)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la mise à jour de l'utilisateur {user_id}: {e}"
            )
            return None
        else:
            return UserMapper.entity_to_dto(user)

    def delete(self, user_id: int) -> int | None:
        try:
            user = self.find_one_entity(user_id)
            if user is None:
                return None
            user.soft_delete()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la suppression de l'utilisateur {user_id}: {e}"
            )
            return None
        else:
            return user_id

    def login(self, form: UserLoginForm) -> UserDTO | None:
        try:
            user = self.find_one_entity_by(name=form.name.data)
            if user is None:
                self.__hasher.hash(form.password.data)
                return None
            self.__hasher.verify(user.password, form.password.data)
            if self.__hasher.check_needs_rehash(user.password):
                user.password = self.__hasher.hash(form.password.data)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la vérification du login de {form.name}: {e}"
            )
            return None
        else:
            return UserMapper.entity_to_dto(user)
