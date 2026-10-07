from app import app
from flask import flash, redirect, url_for, render_template
from app.framework.decorators.inject import inject
from app.services.ticket_status_history_service import TicketStatusHistoryService
from app.framework.service.abstract_auth_service import AbstractAuthService
from app.framework.decorators.auth_required import auth_required
from app.services.user_service import UserService

@app.route('/tickets/<ticket_id>/status-history', methods=['GET'])
@auth_required()
@inject
def get_history_by_ticket(
    ticket_id: int,
    ticket_status_history_service: TicketStatusHistoryService,
    auth_service: AbstractAuthService,
    user_service: UserService
):

    status_histories = ticket_status_history_service.find_all_by(ticket_id=ticket_id)

    if not status_histories:
        app.logger.error(f"Error | get history by ticket impossible")
        flash(f"Impossible de renvoyer l'historique du ticket {ticket_id}", "error")
        return redirect(url_for("ticket_detail", ticket_id=ticket_id))

    users = user_service.find_all()

    authors_map =  {
        user.user_id: f"{user.firstname} {user.lastname}" for user in users
    }

    return render_template(
        "ticket_status_histories/status-history.html",
        status_histories= status_histories,
        ticket_id= ticket_id,
        authors_map= authors_map
    )

