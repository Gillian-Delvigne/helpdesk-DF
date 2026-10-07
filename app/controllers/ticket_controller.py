from app.services.user_service import UserService
from app.framework.decorators.auth_required import auth_required
from app.framework.service import AbstractAuthService
from flask import url_for
from app.forms.users import user_login_form
from app.forms.users import user_login_form
from app.forms.users import user_login_form
from flask import redirect
from flask.helpers import flash
from app.framework.decorators.inject import inject
from app.services.auth_service import AuthService
from flask import jsonify
from app.models.ticket import Ticket
from flask import render_template
from app import app, csrf
from app.forms.tickets.ticket_form import TicketForm
from app.services.ticket_service import TicketService
from app.services.category_service import CategoryService
from app.services.priority_service import PriorityService
from flask import request
from app.models.ticket_status import TicketStatusEnum


# Temporary import
from app.models.equipment import Equipment

@app.route("/tickets/create", methods=["GET", "POST"])
@auth_required()
@inject
def create_ticket(
    category_service: CategoryService,
    priority_service: PriorityService,
    ticket_service: TicketService
):
    form = TicketForm()

    # Note for later:
    # WTForms except to recieve (value stored in db, value displayed in html for user)
    # when it comes to select fields.
    form.category_id.choices = [
        (category.category_id, category.category_name) for category in category_service.find_all()
    ]
    form.priority_id.choices = [
        (priority.priority_id, priority.priority_name) for priority in priority_service.find_all()
    ]
    # Line to change with EquipmentService.find_all() once available 
    form.equipment_id.choices = [
        (equipment.equipment_id, equipment.name) for equipment in Equipment.query.all()
    ]


    if form.validate_on_submit():
        ticket_service.insert(form)
        return "SUCCESS", 201
    return render_template("tickets/create.html", form=form)

@app.route("/tickets", methods=["POST","GET"])
@auth_required("TECHNICIEN")
@inject
def display_all_tickets(
    ticket_service: TicketService
):
    tickets = ticket_service.find_all()
    return render_template("tickets/display_all.html", tickets=tickets)  


# Display tickets of currently connected user
@app.route("/tickets/user", methods=["POST", "GET"])
@auth_required()
@inject
def display_user_tickets(
    auth_service: AbstractAuthService,
    ticket_service: TicketService
    ):

    current_user = auth_service.get_current_user()
    if current_user is None:
        flash("You must be logged in to display your tickets", "warning")
        return redirect(url_for("login"))
     
    tickets = ticket_service.find_all_by(author_id=current_user.user_id)
    return render_template("tickets/display_all.html", tickets=tickets)


# Detail view for one speficic ticket
@app.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@auth_required() #should be owner of the ticket or any technician ?
@inject
def ticket_detail(
    ticket_service: TicketService,
    user_service: UserService,
    ticket_id: int
):
    ticket = ticket_service.find_one(ticket_id)

    if ticket is None:
        flash("Ticket not found", "warning")
        return redirect(url_for("display_all_tickets"))

    author_id = ticket.ticket_author_id
    author = user_service.find_one(author_id)

    return render_template("tickets/detail.html", ticket=ticket, author=author)

@app.route('/tickets/<ticket_id>/update-status', methods=["POST"])
@auth_required()
@inject
def update_ticket_status(
    ticket_id: int,
    auth_service: AbstractAuthService,
    ticket_service: TicketService
):

    new_status = request.form.get("status")

    if new_status not in TicketStatusEnum.values():
        flash("Status de ticket invalide", "warning")
        return redirect(url_for('display_user_tickets'))

    current_user = auth_service.get_current_user()

    update_status = ticket_service.update_ticket_status(ticket_id, TicketStatusEnum[new_status].value, current_user.user_id)

    if update_status is None:
        flash("Impossible de changer le status du ticket", "error")
        return redirect(url_for('display_user_tickets'))

    flash("Le changement de status a été effectué avec succès", "success")
    return redirect(url_for('display_user_tickets'))



#update and delete ticket services
@app.route("/tickets/<int:ticket_id>", methods=["POST","GET"])
@auth_required("TECHNICIEN")
@inject
def update_ticket(
    ticket_service: TicketService,
    ticket_id: int
):
    ticket = ticket_service.find_one(ticket_id)

    if ticket is None:
        flash("Ticket not found", "warning")
        return redirect(url_for("display_all_tickets"))

    return render_template("tickets/update.html", ticket=ticket)