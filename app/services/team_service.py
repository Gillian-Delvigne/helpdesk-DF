from app import app, db
from sqlalchemy.exc import SQLAlchemyError
from app.framework.decorators.injectable import injectable
from app.framework.decorators.inject import inject
from app.framework.injector import Scope
from app.framework.service.abstract_service import AbstractService
from app.models.team import Team
from app.dtos.team_dto import TeamDTO
from app.mappers.team_mapper import TeamMapper
from app.forms.teams.team_form import TeamCreationForm
from app.services.user_service import UserService


@injectable(scope=Scope.SCOPED)
class TeamService(AbstractService):
    @inject
    def __init__(self, user_service: UserService):
        self.__user_service = user_service

    def find_all(self) -> list[TeamDTO]:
        try:
            teams = Team.query.filter_by(active=True).order_by(Team.team_id).all()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la sélection de toutes les équipes: {e}")
            return []
        else:
            return [TeamMapper.entity_to_dto(team) for team in teams]

    def find_one_entity(self, team_id: int):
        try:
            return db.session.get(Team, team_id)
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'équipe, id {team_id}: {e}"
            )
            return None

    def find_one(self, team_id: int) -> TeamDTO:
        try:
            team = db.session.get(Team, team_id)
            return TeamMapper.entity_to_dto(team) if team is not None else None
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'équipe, id {team_id}: {e}"
            )
            return None

    def find_one_by(self, **kwargs) -> TeamDTO:
        try:
            team = Team.query.filter_by(**kwargs).first()
            return TeamMapper.entity_to_dto(team) if team is not None else None
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la récupération de l'équipe (DTO) avec {[f'{k} = {v}' for k, v in kwargs.items()]} : {e}"
            )
            return None

    def insert(self, form: TeamCreationForm) -> TeamDTO | None:
        try:
            team = Team()
            TeamMapper.form_to_entity(form, team)
            team.members = self.__user_service.find_entities_by_ids(form.members.data)
            db.session.add(team)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la création de l'équipe: {e}")
            return None
        else:
            return TeamMapper.entity_to_dto(team)

    def update(self, team_id: int, data) -> TeamDTO | None:
        try:
            team = self.find_one_entity(team_id)
            if team is None:
                return None
            TeamMapper.form_to_entity(data, team)
            team.members = self.__user_service.find_entities_by_ids(data.members.data)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la mise à jour de l'équipe {team_id}: {e}"
            )
            return None
        else:
            return TeamMapper.entity_to_dto(team)

    def delete(self, team_id: int) -> TeamDTO | None:
        try:
            team = self.find_one_entity(team_id)
            if team is None:
                return None
            team.soft_delete()
            team.members.clear()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la suppression de l'équipe {team_id}: {e}"
            )
            return None
        else:
            return TeamMapper.entity_to_dto(team)

    def hard_delete(self, team_id: int) -> int | None:
        try:
            team = self.find_one_entity(team_id)
            if team is None:
                return None
            db.session.delete(team)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(
                f"Erreur lors de la suppression de l'équipe {team_id}: {e}"
            )
            return None
        else:
            return team_id
