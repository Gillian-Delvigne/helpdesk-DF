from app.framework.dto import AbstractDTO
from app.dtos.user_dto import UserDTO
from app.models.team import Team


class TeamDTO(AbstractDTO):
    def __init__(self):
        super().__init__()
        self.team_id = None
        self.name = None
        self.description = None
        self.members = []

    @staticmethod
    def build_from_entity(team: Team) -> "TeamDTO":
        team_dto = TeamDTO()
        team_dto.team_id = team.team_id
        team_dto.name = team.name
        team_dto.description = team.description
        team_dto.members = [
            UserDTO.build_from_entity(member) for member in team.members
        ]
        return team_dto

    def get_json_parsable(self):
        data = dict(self.__dict__)
        data["members"] = [member.get_json_parsable() for member in self.members]
        return data
