from app.framework.mapper import AbstractMapper
from app.models.equipment import Equipment
from app.dtos.equipment_dto import EquipmentDTO

class EquipmentMapper(AbstractMapper):

    @staticmethod
    def entity_to_dto(entity: Equipment) -> EquipmentDTO:
        return EquipmentDTO.build_from_entity(entity)
        