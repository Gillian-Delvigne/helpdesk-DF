from flask import redirect, render_template, request, flash, url_for

from app import app
from app.framework.decorators.inject import inject
from app.framework.decorators.auth_required import auth_required
from app.forms.users.user_register_form import UserRegisterForm
from app.forms.users.user_login_form import UserLoginForm
from app.services.user_service import UserService
from app.framework.service.abstract_auth_service import AbstractAuthService
from app.dtos.user_dto import UserDTO


# Utils -----------------------------------------------------------------------
def dashboard_route_for(user: UserDTO) -> str:
    if user.is_admin() or user.has_role("TECHNICIEN"):
        return "/dashboard"
    return "/client-dashboard"


# Endpoints -------------------------------------------------------------------


@app.route("/register", methods=["GET", "POST"])
@inject
def register(user_service: UserService, auth_service: AbstractAuthService):
    if current_user := auth_service.get_current_user():
        return redirect(dashboard_route_for(current_user))
    form = UserRegisterForm()
    if form.validate_on_submit():
        user = user_service.insert(form)
        if user is not None:
            auth_service.login(user)
            return redirect(dashboard_route_for(user))
    return render_template("users/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
@inject
def login(user_service: UserService, auth_service: AbstractAuthService):
    if current_user := auth_service.get_current_user():
        return redirect(dashboard_route_for(current_user))
    form = UserLoginForm()
    error = None
    if form.validate_on_submit():
        user = user_service.login(form)
        if user is not None:
            auth_service.login(user)
            dest = request.args.get("next")
            if dest is not None and dest.startswith("/") and not dest.startswith("//"):
                return redirect(dest)
            return redirect(dashboard_route_for(user))
        else:
            error = "Identifiant ou mot de passe incorrect"
    return render_template("users/login.html", form=form, error=error)


@app.route("/logout", methods=["GET"])
@inject
def logout(auth_service: AbstractAuthService):
    auth_service.logout()
    return redirect("/")


@app.route("/dashboard", methods=["GET", "POST"])
@auth_required(role_name="TECHNICIEN")
def goToDashboard():
    return render_template("dashboard/dashboard.html")


@app.route("/client-dashboard", methods=["GET", "POST"])
@auth_required()
def goToClientDashboard():
    return render_template("dashboard/client-dashboard.html")


@app.route("/users/list")
@auth_required(role_name="ADMIN")
@inject
def list_users(user_service: UserService):
    users = user_service.find_all(active=False)
    return render_template("users/list.html", users=users)


@app.route("/users/add", methods=["GET", "POST"])
@auth_required(role_name="ADMIN")
@inject
def create_user(user_service: UserService):
    form = UserRegisterForm()
    if form.validate_on_submit():
        user = user_service.insert(form)
        if user is not None:
            flash(f"L'utilisateur {user.name} a été créé correctement.", "success")
            return redirect(url_for("list_users"))
    return render_template("users/add_user.html", form=form)


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@auth_required(is_current_user=True)
@inject
def edit_profile(user_service: UserService, user_id=None):
    if user_id is not None:
        app.logger.debug(f"user id = {user_id}")
    else:
        app.logger.debug("No user id provided")
    return render_template("users/update_user.html")
