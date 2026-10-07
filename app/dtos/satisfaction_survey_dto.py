from app.framework.dto import AbstractDTO
from app.dtos.ticket_dto import TicketDTO
from app.dtos.user_dto import UserDTO
from app.models.satisfaction_survey import SatisfactionSurvey


class SatisfactionSurveyDTO(AbstractDTO):

    def __init__(self) -> None:
        super().__init__()
        self.survey_id = None
        self.rating = None
        self.comment = None
        self.ticket: TicketDTO = None
        self.client: list[UserDTO] = []


    @staticmethod
    def build_from_entity(entity: SatisfactionSurvey) -> "SatisfactionSurveyDTO": # type: ignore
        survey_dto = SatisfactionSurveyDTO()

        survey_dto.survey_id = entity.survey_id
        survey_dto.rating = entity.rating
        survey_dto.comment = entity.comment

        survey_dto.ticket = TicketDTO.build_from_entity(entity.ticket)
        survey_dto.client = [UserDTO.build_from_entity(survey_client) for survey_client in entity.client]

        return survey_dto

    def get_json_parsable(self):
        data = dict(self.__dict__)
        data['ticket'] = self.ticket.get_json_parsable()
        data['client'] = [client.get_json_parsable() for client in self.client]
