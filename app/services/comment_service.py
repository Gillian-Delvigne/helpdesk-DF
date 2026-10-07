from app import db
from app import app
from app.framework.service.abstract_service import AbstractService
from app.models.comment import Comment
from app.mappers.comment_mapper import CommentMapper
from app.framework.decorators.injectable import injectable

@injectable
class CommentService(AbstractService):

    def find_all(self):
        """Tous les commentaires."""
        try:
            comments = Comment.query.all()

            return [CommentMapper.entity_to_dto(comment) for comment in comments]

        except Exception as e:
            app.logger.error(f"Error | find_all comments: {e}")
            return None
            # db.session.rollback() pas nécessaire car juste un appel à la db

    def find_one_entity(self, entity_id):
        """Un commentaire sous forme d'entité"""
        try:
            comment = db.session.get(Comment, entity_id)

            if comment is None:
                return None

            return comment
        
        except Exception as e:
            app.logger.error(f"Error | find_one_entity comment: {e}")
            return None
    
    def find_one(self, entity_id: int):
        """Un commentaire par son Id."""
        try:
            comment = db.session.get(Comment, entity_id)

            if comment is None:
                return None
            
            return CommentMapper.entity_to_dto(comment)

        except Exception as e:
            app.logger.error(f"Error | find_one comment: {e}")
            return None
            # db.session.rollback() pas nécessaire car juste un appel à la db

    def find_one_by(self, **kwargs):
        """Un commentaire sur base d'un critère (exemple ticket_id)."""
        try:
            comment = Comment.query.filter_by(**kwargs).one_or_none()

            if comment is None:
                return None

            return CommentMapper.entity_to_dto(comment)

        except Exception as e:
            app.logger.error(f"Error | find_one_by comment: {e}")
            return None
            # db.session.rollback() pas nécessaire car juste un appel à la db

    def find_all_by(self, **kwargs):
        """Tous les commentaires sur base d'un critère (exemple  ticket_id)"""
        try:

            comments = Comment.query.filter_by(**kwargs).all()

            if comments is None:
                return None

            return [CommentMapper.entity_to_dto(comment) for comment in comments]

        except Exception as e:
            app.logger.error(f"Error | find_all_by comment: {e}")
            return None

    def insert(self, data):
        """Crée un commentaire à partir d'un formulaire validé."""
        try:
            form = data['form']
            author_id = data['author_id']
            ticket_id = data['ticket_id']

            comment = Comment()

            comment = CommentMapper.form_to_entity(
                form, 
                comment, 
                author_id, 
                ticket_id)

            db.session.add(comment)
            db.session.commit()

            return CommentMapper.entity_to_dto(comment)

        except Exception as e:
            app.logger.error(f"Error | insert comment: {e}")
            db.session.rollback()
            return None            


    def update(self, entity_id: int, data):
        """Met à jour un commentaire existant."""

        try:
            comment = db.session.get(Comment, entity_id)

            if comment is None:
                return None

            form = data['form']
            author_id = data['author_id']
            ticket_id = data['ticket_id']

            comment = CommentMapper.form_to_entity(form, comment, author_id, ticket_id)

            db.session.commit()

            return CommentMapper.entity_to_dto(comment)


        except Exception as e:
            app.logger.error(f"Error | update comment: {e}")
            db.session.rollback()
            return None

    def delete(self, entity_id: int):
        """Supprime un commentaire."""

        try:
            comment = db.session.get(Comment, entity_id)

            if comment is None:
                return None

            db.session.delete(comment)
            db.session.commit()

            app.logger.debug(f"Le commentaire {entity_id} a bien été supprimé")
            return True
        
        except Exception as e:
            app.logger.error(f"Error | delete comment: {e}")
            db.session.rollback()
            return None