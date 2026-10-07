import os, uuid
from app.framework.service.abstract_service import AbstractService
from app import app, db
from app.models.attachment import Attachment
from app.mappers.attachment_mapper import AttachmentMapper
from app.framework.decorators.injectable import injectable
from flask import current_app
from werkzeug.utils import secure_filename

@injectable
class AttachmentService(AbstractService):

    ALLOWED_EXTENSIONS = {
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "gif",
        "txt",
        "doc",
        "docx",
        "xls",
        "xlsx"
    }

    ALLOWED_MIME_TYPES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/gif",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024 #10MB

    def find_all(self):
        """Toutes les pièces jointes (sous forme de DTO)."""

        try:
            attachments = Attachment.query.all()

            return [AttachmentMapper.entity_to_dto(attachment) for attachment in attachments]

        except Exception as e:
            app.logger.error(f"Error |find all attachment : {e}")
            return None

    def find_all_by(self, **kwargs):
        """Toutes les pièces jointes selon un critère."""

        try:
            attachments = Attachment.query.filter_by(**kwargs).all()

            if attachments is None:
                return None

            return [AttachmentMapper.entity_to_dto(attachment) for attachment in attachments]

        except Exception as e:
            app.logger.error(f" Error | find all by attachment : {e} ")
            return None    

    def find_one_entity(self, entity_id: int):
        """Une pièce jointe par sa clé primaire, ou None.""" 

        try:
            attachment = db.session.get(Attachment, entity_id)

            if attachment is None:
                return None

            return attachment

        except Exception as e:
            app.logger.error(f"Error |find all attachment : {e}")
            return None 

    def find_one(self, entity_id: int):
        """Un DTO de la pièce jointe par sa clé primaire, ou None."""  

        try:
            attachment = db.session.get(Attachment, entity_id)
            
            if attachment is None:
                return None

            return AttachmentMapper.entity_to_dto(attachment)
        
        except Exception as e:
            app.logger.error(f"Error |find all attachment : {e}")
            return None 

    def find_one_by(self, **kwargs):
        """Une pièce jointe sur base d'un critère (exemple ticket_id)."""   
        try:
            attachment = Attachment.query.filter_by(**kwargs).one_or_none()

            if attachment is None:
                return None

            return AttachmentMapper.entity_to_dto(attachment)
        
        except Exception as e:
            app.logger.error(f"Error |find all attachment : {e}")
            return None

    def _validate_file(self, file_data):
        """Valider le fichier avant son enregistrement"""

        if not file_data:
            return False, "Aucun fichier"
        if not file_data.filename:
            return False, "Aucun nom de fichier"

        filename = secure_filename(file_data.filename)

        if not filename:
            return False, "Nom de fichier invalide"

        extension = os.path.splitext(filename)[1].lower().lstrip(".")

        if extension not in self.ALLOWED_EXTENSIONS:
            return False, "Type de fichier non autorisé"

        if file_data.mimetype not in self.ALLOWED_MIME_TYPES:
            return False, "Type MIME non autorisé"

        file_data.stream.seek(0, os.SEEK_END)
        file_size = file_data.stream.tell()
        file_data.stream.seek(0)

        if file_size > self.MAX_FILE_SIZE:
            return False, "Fichier trop volumineux (max 10 MB)"
        if file_size == 0:
            return False, "Le fichier est vide"

        return True, None

    def insert(self, data):
        """Crée une pièce jointe à partir d'un formulaire validé."""

        absolute_path = None 
        
        try:
            form= data['form']
            author_id = data['author_id']
            ticket_id = data['ticket_id']

            file_data = form.attachment.data

            # Validation de la pièce jointe envoyé via le formulaire

            is_valid, error_message = self._validate_file(file_data)

            if not is_valid:
                app.logger.error(f"Error | attachment validation error: {error_message}")
                return None

            # Nom original

            original_filename = secure_filename(file_data.filename)

            extension =  os.path.splitext(original_filename)[1]

            # Nom de stockage aléatoire

            stored_filename= f"{uuid.uuid4()}{extension}"

            # Chemin relatif stocké en DB

            relative_path = os.path.join("uploads", "attachments", stored_filename)

            # Dossier privé

            upload_folder = os.path.join(current_app.root_path, "uploads", "attachments")

            os.makedirs(upload_folder, exist_ok=True)

            # Sauvegarde

            absolute_path = os.path.join(upload_folder, stored_filename)

            file_data.save(absolute_path)

            # Double vérification de la taille de fichier

            file_size = os.path.getsize(absolute_path)

            if file_size > self.MAX_FILE_SIZE:
                os.remove(absolute_path)
                return None

            # DB

            attachment = Attachment()

            attachment = AttachmentMapper.form_to_entity(
                form,
                attachment,
                author_id,
                ticket_id,
                original_filename,
                relative_path,
                file_size 
            )

            db.session.add(attachment)
            db.session.commit()

            return AttachmentMapper.entity_to_dto(attachment)

        except Exception as e:
            app.logger.error(f"Error | insert attachement: {e}")
            db.session.rollback()

            if absolute_path and os.path.exists(absolute_path):
                os.remove(absolute_path)

            return None
          
    def get_file_path(self, entity_id: int):
        """
        Retourne le chemin absolu uniquement si la pièce jointe existe en DB
        et que le fichier existe réellement dans uploads
        """

        attachement = db.session.get(Attachment, entity_id)

        if attachement is None:
            return None

        upload_root = os.path.realpath(
            os.path.join(
                current_app.root_path,
                "uploads",
                "attachments"
            )
        )

        file_path = os.path.realpath(
            os.path.join(
                current_app.root_path,
                attachement.attachment_path
            )
        )

        if not file_path.startswith(upload_root + os.sep):
            app.logger.warning(f"Attachment path invalid for attachment {entity_id}")
            return None

        if not os.path.isfile(file_path):
            return None

        return file_path

    def download(self, entity_id: int):
        """téléchargement physique d'une pièce jointe"""
        try:
            file_path = self.get_file_path(entity_id)

            if file_path is None:
                return None

            attachment = db.session.get(Attachment, entity_id)

            return {
                "path": file_path,
                "filname": attachment.attachment_filename
            }
        
        except Exception as e:
            app.logger.error(f"Error | download attachement: {e}")
            return None 
            

        
    def update(self, entity_id: int, data):
        """Met à jour une pièce jointe existante."""

        try:
            attachment =  db.session.get(Attachment, entity_id)

            if attachment is None:
                return None

            form = data['form']
            author_id = data['author_id']
            ticket_id = data['ticket_id']

            attachment = AttachmentMapper.form_to_entity(form, attachment, author_id, ticket_id)

            db.session.commit()

            return AttachmentMapper.entity_to_dto(attachment) 
        
        except Exception as e:
            app.logger.error(f"Error | update attachement: {e}")
            db.session.rollback()
            return None  

    def delete(self, entity_id: int):
        """Supprime une pièce."""
        try:
            attachment = db.session.get(Attachment, entity_id)

            if attachment is None:
                return None

            absolute_path = os.path.join(current_app.root_path, attachment.attachment_path)

            if os.path.exists(absolute_path):
                os.remove(absolute_path)

            db.session.delete(attachment)
            db.session.commit()

            app.logger.debug(f"La pièce jointe {entity_id} a bien été supprimée.")
            return True
        
        except Exception as e:
            app.logger.error(f"Error | delete attachement: {e}")
            db.session.rollback()
            return None  