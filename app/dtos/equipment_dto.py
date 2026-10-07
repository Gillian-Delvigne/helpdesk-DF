from app.framework.dto import AbstractDTO
from app.dtos.user_dto import UserDTO
from app.dtos.site_dto import SiteDTO
from models.equipment import Equipment


class EquipmentDTO(AbstractDTO):

    def __init__(self) -> None:
        super().__init__()
        self.equipment_id = None
        self.name = None
        self.type = None
        self.serial = None
        self.purchase_date = None
        self.site: SiteDTO = None            # SiteDTO
        self.user: UserDTO = None            # UserDTO

    @staticmethod
    def build_from_entity(entity: Equipment) -> "EquipmentDTO": # type: ignore
        equipment_dto = EquipmentDTO()

        equipment_dto.equipment_id = entity.equipment_id
        equipment_dto.name = entity.name
        equipment_dto.type = entity.type
        equipment_dto.serial = entity.serial
        equipment_dto.purchase_date = entity.purchase_date

        equipment_dto.site = SiteDTO.build_from_entity(entity.site)
        equipment_dto.user = UserDTO.build_from_entity(entity.user) if entity.user else None

        return equipment_dto

    def get_json_parsable(self): # type: ignore
        data = dict(self.__dict__)
        data['site'] = self.site.get_json_parsable()
        data['user'] = self.user.get_json_parsable() if self.user else None
        return data
