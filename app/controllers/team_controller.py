from flask import redirect, render_template, flash, url_for

from app import app
from app.framework.decorators.inject import inject
from app.framework.decorators.auth_required import auth_required
from app.forms.teams.team_form import TeamCreationForm
from app.services.user_service import UserService
from app.services.team_service import TeamService


@app.route("/teams")
@auth_required(role_name="ADMIN")
@inject
def team_list(team_service: TeamService):
    teams = team_service.find_all()
    return render_template("teams/list.html", teams=teams)


@app.route("/teams/add", methods=["GET", "POST"])
@app.route("/teams/<int:team_id>/edit", methods=["GET", "POST"])
@auth_required(role_name="ADMIN")
@inject
def create_team(team_service: TeamService, user_service: UserService, team_id=None):
    team = team_service.find_one(team_id) if team_id else None
    users = [
        user
        for user in user_service.find_all()
        if (
            user.has_role("TECHNICIEN")
            and (
                user.team_id is None
                or (team is not None and user.team_id == team.team_id)
            )
        )
    ]

    users_by_id = {user.user_id: user for user in users}

    if team_id and team is None:
        flash("Équipe introuvable.", "warning")
        return redirect(url_for("team_list"))

    form = TeamCreationForm(obj=team)

    form.members.choices = [
        (user.user_id, f"{user.firstname} {user.lastname}") for user in users
    ]
    if team is not None and not form.is_submitted():
        form.members.data = [member.user_id for member in team.members]

    members_data = [(subfield, users_by_id[subfield.data]) for subfield in form.members]

    if form.validate_on_submit():
        if team is None:
            team = team_service.insert(form)
            if team is not None:
                flash(f"L'équipe {team.name} a été créée correctement.", "success")
                return redirect(url_for("team_list"))
        else:
            team = team_service.update(team_id, form)
            if team is not None:
                flash(
                    f"L'équipe {team.name} a été mise à jour correctement.", "success"
                )
                return redirect(url_for("team_list"))
    return render_template(
        "teams/add_or_update.html",
        form=form,
        team=team,
        members_data=members_data,
    )


@app.route("/teams/<int:team_id>/delete", methods=["POST"])
@auth_required(role_name="ADMIN")
@inject
def delete_team(team_service: TeamService, team_id=None):
    if team_id is None:
        flash("Id d'équipe invalide.", "error")
        return redirect(url_for("team_list"))
    deleted_team_id = team_service.hard_delete(team_id)
    if deleted_team_id is None:
        flash(f"Erreur lors de la suppression de l'équipe {team_id}.", "error")
        return redirect(url_for("team_list"))
    flash("L'équipe a été supprimée correctement.", "success")
    return redirect(url_for("team_list"))
