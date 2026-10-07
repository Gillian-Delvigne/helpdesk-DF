from app.dtos.category_dto import CategoryDTO
from app.forms.categories.category_form import CategoryForm
from app.framework.mapper import AbstractMapper
from app.models.category import Category

class CategoryMapper(AbstractMapper):
    @staticmethod
    def entity_to_dto(category: Category) -> CategoryDTO:
        return CategoryDTO.build_from_entity(category)
    
    @staticmethod
    def form_to_entity(form, category: Category) -> Category:
        if isinstance(form, CategoryForm):
            category.name = form.name.data
            category.description = form.description.data
        return category
