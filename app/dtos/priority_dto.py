from app.models.priority import Priority
from app.framework.dto import AbstractDTO


class PriorityDTO(AbstractDTO):
    
    def __init__(self):
        super().__init__()
        self.priority_id = None
        self.priority_name = None
        self.priority_level = None
        self.priority_delay_hours = None

    @staticmethod
    def build_from_entity(priority: Priority) -> "PriorityDTO":
        priority_dto = PriorityDTO()

        priority_dto.priority_id = priority.priority_id
        priority_dto.priority_name = priority.name
        priority_dto.priority_level = priority.level
        priority_dto.priority_delay_hours = priority.delay_hours

        return priority_dto
    
    def get_json_parsable(self):
        data = dict(self.__dict__)
        return data