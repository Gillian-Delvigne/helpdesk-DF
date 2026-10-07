from app.framework.mapper import AbstractMapper
from app.models.site import Site
from app.dtos.sites_dto import SiteDTO

class EquipmentMapper(AbstractMapper):

    @staticmethod
    def entity_to_dto(entity: Site) -> SiteDTO:
        return SiteDTO.build_from_entity(entity)