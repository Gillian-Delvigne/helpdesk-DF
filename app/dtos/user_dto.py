from app.framework.dto import AbstractDTO
from app.dtos.role_dto import RoleDTO
from app.models.user import User


class UserDTO(AbstractDTO):
    def __init__(self):
        super().__init__()
        self.user_id = None
        self.name = None
        self.email = None
        self.firstname = None
        self.lastname = None
        self.team_id = None
        self.site_id = None
        self.roles = []

    @staticmethod
    def build_from_entity(user: User) -> "UserDTO":
        user_dto = UserDTO()
        user_dto.user_id = user.user_id
        user_dto.name = user.name
        user_dto.email = user.email
        user_dto.firstname = user.firstname
        user_dto.lastname = user.lastname
        user_dto.team_id = user.team_id
        user_dto.site_id = user.site_id
        user_dto.roles = [RoleDTO.build_from_entity(ur.rel_role) for ur in user.roles]
        user_dto.active = user.active
        user_dto.created_at = user.created_at
        user_dto.updated_at = user.updated_at
        user_dto.deleted_at = user.deleted_at
        return user_dto

    def get_json_parsable(self):
        data = dict(self.__dict__)
        data["roles"] = [role.get_json_parsable() for role in self.roles]
        return data

    def is_admin(self) -> bool:
        return "ADMIN" in self.role_names()

    def has_role(self, rolename: str) -> bool:
        return rolename in self.role_names()

    # --- Utils ---------------------------------------------------------------

    def role_names(self) -> list[str]:
        return [role.name for role in self.roles]
