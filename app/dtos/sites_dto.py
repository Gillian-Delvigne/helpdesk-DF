from app.framework.dto import AbstractDTO
from app.dtos.user_dto import UserDTO
from app.dtos.equipment_dto import EquipmentDTO
from app.models.site import Site


class SiteDTO(AbstractDTO):

    def __init__(self):
        super().__init__()
        self.site_id = None
        self.name = None
        self.address = None
        self.city = None
        self.users = []
        self.equipments = []

    @staticmethod
    def build_from_entity(entity: Site) -> "SiteDTO":
        site_dto = SiteDTO()
        site_dto.site_id = entity.site_id
        site_dto.name = entity.name
        site_dto.address = entity.address
        site_dto.city = entity.city

        site_dto.users = [UserDTO.build_from_entity(user) for user in entity.users]
        site_dto.equipments = [EquipmentDTO.build_from_entity(equipment) for equipment in entity.equipments]

        return site_dto

    def get_json_parsable(self):
        data = dict(self.__dict__)
        data["users"] = [user.get_json_parsable() for user in self.users]
        data["equipments"] = [equipment.get_json_pasable() for equipment in self.equipments]
        