from app.framework.dto import AbstractDTO
from app.models.role import Role


class RoleDTO(AbstractDTO):
    def __init__(self):
        super().__init__()
        self.role_id = None
        self.name = None

    @staticmethod
    def build_from_entity(role: Role) -> "RoleDTO":
        role_dto = RoleDTO()
        role_dto.role_id = role.role_id
        role_dto.name = role.name
        return role_dto

    def get_json_parsable(self):
        return dict(self.__dict__)
