from app.framework.decorators.injectable import injectable
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from app.framework.service.abstract_service import AbstractService
from app.dtos.priority_dto import PriorityDTO
from app.forms.priorities.priority_form import PriorityForm
from app.mappers.priority_mapper import PriorityMapper
from app.models.priority import Priority

@injectable
class PriorityService(AbstractService):
    def insert(self, form: PriorityForm) -> PriorityDTO | None:
        try:
            priority = Priority()
            PriorityMapper.form_to_entity(form, priority)

            db.session.add(priority)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la création de la priorité: {e}")
            return None
        else:
            return PriorityMapper.entity_to_dto(priority)

    def find_all(self):
        try:
            priorities = Priority.query.all()
            return [PriorityMapper.entity_to_dto(p) for p in priorities]
        except SQLAlchemyError as e:
            app.logger.error(f"Erreur lors de la récupération des priorités: {e}")
            return None

    def find_one(self, entity_id: int):
        pass

    def find_one_entity(self, entity_id: int):
        pass

    def find_one_by(self, **kwargs):
        pass

    def update(self, entity_id: int, data):
        pass

    def delete(self, entity_id: int):
        pass
