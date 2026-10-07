from app.framework.mapper import AbstractMapper
from app.models.satisfaction_survey import SatisfactionSurvey
from app.dtos.satisfaction_survey_dto import SatisfactionSurveyDTO

class EquipmentMapper(AbstractMapper):

    @staticmethod
    def entity_to_dto(entity: SatisfactionSurvey) -> SatisfactionSurveyDTO:
        return SatisfactionSurveyDTO.build_from_entity(entity)
        