from app.dtos.team_dto import TeamDTO
from app.framework.mapper import AbstractMapper
from app.models.team import Team
from app.forms.teams.team_form import TeamCreationForm


class TeamMapper(AbstractMapper):
    @staticmethod
    def entity_to_dto(team: Team) -> TeamDTO:
        return TeamDTO.build_from_entity(team)

    @staticmethod
    def form_to_entity(form, team: Team) -> Team:
        if isinstance(form, TeamCreationForm):
            team.name = form.name.data
            team.description = form.description.data
        return team
