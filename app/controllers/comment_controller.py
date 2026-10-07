from app import app
from flask import flash, redirect, url_for, render_template, request
from flask_wtf import FlaskForm
from app.services.comment_service import CommentService
from app.framework.service.abstract_auth_service import AbstractAuthService
from app.forms.comment_form import CommentForm
from app.framework.decorators.inject import inject
from app.services.user_service import UserService
from app.framework.decorators.auth_required import auth_required

@app.route('/tickets/<ticket_id>/comments/create', methods=['GET', 'POST'])
@auth_required()
@inject
def comment_create(
    ticket_id: int,
    comment_service: CommentService,
    auth_service: AbstractAuthService
):
    """Création d'un commentaire sur un ticket"""

    current_user = auth_service.get_current_user()
    
    form = CommentForm()

    if form.validate_on_submit():

        data = {
            "form": form,
            "author_id": current_user.user_id,
            "ticket_id": ticket_id
        }

        comment = comment_service.insert(data)

        if comment is None:
            app.logger.error(f"Error | comment create impossible")
            flash("Impossible de créer le commentaire.", "error")
        
        else:
            flash("Commentaire ajouté avec succès.", "success")
            return redirect(url_for(
                "comment_list",
                ticket_id=ticket_id
            ))
        
    return render_template(
        "comments/create.html",
        form=form,
        ticket_id=ticket_id
    )

@app.route('/tickets/<ticket_id>/comments', methods=['GET'])
@auth_required()
@inject
def comment_list(
    ticket_id: int,
    comment_service: CommentService,
    user_service: UserService
):
    """Lister tous les commentaires d'un ticket"""

    form = CommentForm()

    comments = comment_service.find_all_by(ticket_id=ticket_id)

    if comments is None:
        app.logger.error(f"Error | comment list impossible")
        comments = []

    users = user_service.find_all()

    authors_map = {
        user.user_id: f"{user.firstname} {user.name}" for user in users
    }

    return render_template(
        'comments/list.html',
        ticket_id=ticket_id,
        comments=comments,
        form=form,
        authors_map= authors_map
    )


@app.route('/tickets/<ticket_id>/comments/<comment_id>/edit', methods=['GET', 'POST'])
@auth_required()
@inject
def comment_edit(
    ticket_id: int,
    comment_id: int,
    comment_service: CommentService,
    auth_service: AbstractAuthService,
):
    """Modifier le commentaire d'un ticket"""

    comment = comment_service.find_one(comment_id)

    if comment is None:
        app.logger.error(f"Error | comment find one impossible")
        flash("Impossible de trouver le commentaire.", "error")
        return redirect(url_for(
            "comment_list",
            ticket_id=ticket_id
        ))

    current_user = auth_service.get_current_user()

    if current_user.user_id != comment.author_id:
        flash("Vous n'êtes pas autorisé à modifier ce commentaire", "warning")
        return redirect(url_for(
            "comment_list",
            ticket_id=ticket_id
        ))
    
    form = CommentForm()

    if form.validate_on_submit():

        data = {
            'form': form,
            'author_id': comment.author_id,
            'ticket_id': ticket_id
        }

        update_comment = comment_service.update(comment_id, data)

        if update_comment is None:
            app.logger.error(f"Error | comment update impossible: {comment_id}")
            flash("Impossible de mettre à jour le commentaire.", "error")
        else:
            flash("Commentaire mis à jour avec succès.", "success")
            return redirect(url_for(
                "comment_list",
                ticket_id=ticket_id
            ))
        
    elif request.method == "GET":
        form.comment_content.data = comment.comment_content

    return render_template(
        'comments/edit.html',
        form=form,
        ticket_id=ticket_id,
        comment=form.comment_content
    )
 

@app.route('/tickets/<ticket_id>/comments/<comment_id>/delete', methods=['POST'])
@auth_required()
@inject
def comment_delete(
    ticket_id: int,
    comment_id: int,
    comment_service: CommentService,
    auth_service: AbstractAuthService
):
    """Supprimer le commentaire d'un ticket"""

    comment = comment_service.find_one(comment_id)

    if comment is None:
        app.logger.error(f"Error | comment find one impossible")
        flash("Impossible de trouver le commentaire", "error")
        return redirect(url_for(
            "comment_list",
            ticket_id=ticket_id
        ))

    current_user = auth_service.get_current_user()

    is_author = current_user.user_id == comment.author_id
    is_admin = "admin" in current_user.roles

    if not (is_author or is_admin):
        flash("Vous n'êtes pas autorisé à supprimer ce commentaire", "warning")
        return redirect(url_for(
            "comment_list",
            ticket_id=ticket_id
        ))

    deleted = comment_service.delete(comment_id)

    if deleted is None:
        app.logger.error(f"Error | comment delete impossible : {comment_id}")
        flash("Impossible de supprimer le commentaire", "error")
        return redirect(url_for(
            "comment_list",
            ticket_id=ticket_id
        ))

    flash("Commentaire supprimé avec succès.", "success")

    return redirect(url_for("comment_list", ticket_id=ticket_id))