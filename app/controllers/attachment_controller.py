from app import app
from flask import flash, redirect, url_for, render_template, send_file
from app.framework.decorators.inject import inject
from app.framework.decorators.auth_required import auth_required
from app.services.attachment_service import AttachmentService
from app.forms.attachment_form import AttachmentForm
from app.framework.service.abstract_auth_service import AbstractAuthService


@app.route('/tickets/<ticket_id>/attachments/create', methods=['GET', 'POST'])
@auth_required()
@inject
def attachment_create(
    attachment_service: AttachmentService,
    auth_service: AbstractAuthService,
    ticket_id: int
):
    """Création d'une pièce jointe sur un ticket"""

    form = AttachmentForm()

    if form.validate_on_submit():
        data = {
            "form": form,
            "author_id": auth_service.get_current_user().user_id,
            "ticket_id": ticket_id
        }

        result = attachment_service.insert(data)

        if result is None:
            app.logger.error(f"Error | attachment create impossible")
            flash("Impossible d'ajouter la pièce jointe", "error")

        else:
            flash("La pièce jointe a été ajoutée avec succès", "success")
            return redirect(url_for("attachment_list", ticket_id=ticket_id))

    return render_template(
        "attachments/list.html",
        form= form,
        ticket_id= ticket_id
    )

@app.route('/tickets/<ticket_id>/attachments', methods=['GET'])
@auth_required()
@inject
def attachment_list(
    ticket_id: int,
    attachment_service: AttachmentService,
    auth_service: AbstractAuthService
):
    """Liste toutes les pièces jointes d'un ticket"""
    
    form = AttachmentForm()

    attachments = attachment_service.find_all_by(ticket_id=ticket_id)

    if attachments is None:
        app.logger.error(f"Error | display attachements list impossible")
        flash("Impossible d'afficher la liste des pièces jointes", "error")
        attachments = []

    return render_template(
        'attachments/list.html',
        ticket_id=ticket_id,
        attachments= attachments,
        form= form
    )

@app.route('/tickets/<ticket_id>/attachments/<attachment_id>/delete', methods=['POST'])
@auth_required(is_current_user=True)
@inject
def attachment_delete(
    ticket_id: int,
    attachment_id: int,
    attachment_service: AttachmentService,
    auth_service: AbstractAuthService
):

    attachment = attachment_service.find_one(attachment_id)

    if attachment is None:
        app.logger.error(f"Error | attachment find one impossible")
        flash(f"Impossible de trouver la pièce jointe {attachment_id}", "error")
        return redirect(url_for('attachment_list', ticket_id=ticket_id))

    """Vérification des roles"""

    current_user = auth_service.get_current_user()

    is_author = current_user.user_id == attachment.author_id
    is_admin = "admin" in current_user.roles

    if not is_admin and not is_author:
        flash("Vous n'êtes pas autorisé à supprimer cette pièce jointe", "warning")
        return redirect(url_for('attachment_list', ticket_id=ticket_id))

    """Suppression en db"""

    deleted = attachment_service.delete(attachment_id)

    if deleted is None:
        app.logger.error(f"Error | attachment delete impossible")
        flash(f"Impossible de supprimer la pièce jointe {attachment_id}", "erro")
        return redirect(url_for('attachment_list', ticket_id=ticket_id))

    flash(f"La pièce jointe a été supprimée avec succès.", "success")

    return redirect(url_for('attachment_list', ticket_id=ticket_id))


@app.route('/tickets/<ticket_id>/attachments/<attachment_id>/download', methods=["GET"])
@auth_required()
@inject
def attachment_download(
    ticket_id: int,
    attachment_id: int,
    attachment_service: AttachmentService
):

    file_data = attachment_service.download(attachment_id)

    if file_data is None:
        app.logger.error(f"Error | attachment download impossible")
        flash(f"Impossible de télécharger la pièce jointe {attachment_id}", "error")
        return redirect(url_for('attachment_list', ticket_id=ticket_id))


    return send_file(
        path_or_file=file_data["path"],
        as_attachment=True,
        download_name=file_data["filname"]
    )

     

