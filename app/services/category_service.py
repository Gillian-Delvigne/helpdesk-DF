from app.framework.decorators.injectable import injectable
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from app.framework.service.abstract_service import AbstractService
from app.dtos.category_dto import CategoryDTO
from app.forms.categories.category_form import CategoryForm
from app.mappers.category_mapper import CategoryMapper
from app.models.category import Category

@injectable
class CategoryService(AbstractService):
    def insert(self, form: CategoryForm) -> CategoryDTO | None:
        try:
            category = Category()
            CategoryMapper.form_to_entity(form, category)

            db.session.add(category)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            app.logger.error(f"Erreur lors de la création de la catégorie: {e}")
            return None
        else:
            return CategoryMapper.entity_to_dto(category)

    def find_all(self):
        try:
            categories = Category.query.all()
            return [CategoryMapper.entity_to_dto(c) for c in categories]
        except SQLAlchemyError as e:
            app.logger.error(f"Erreur lors de la récupération des catégories: {e}")
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