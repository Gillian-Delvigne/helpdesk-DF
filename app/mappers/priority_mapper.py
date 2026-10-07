from app.dtos.priority_dto import PriorityDTO
from app.framework.mapper import AbstractMapper
from app.models.priority import Priority
from app.forms.priorities.priority_form import PriorityForm

class PriorityMapper(AbstractMapper):
    @staticmethod
    def entity_to_dto(priority: Priority) -> PriorityDTO:
        return PriorityDTO.build_from_entity(priority)
    
    @staticmethod
    def form_to_entity(form, priority: Priority) -> Priority:
        if isinstance(form, PriorityForm):
            priority.name = form.name.data
            priority.level = form.level.data
            priority.delay_hours = form.delay_hours.data
        return priority