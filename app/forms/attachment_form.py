from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired


class AttachmentForm(FlaskForm):

    attachment = FileField(
        "Fichier",
        validators=[
            FileRequired(message="Veuillez sélectionner un fichier."),
            FileAllowed(
                ["pdf", "png", "jpg", "jpeg", "docx"],
                "Type de fichier non autorisé."
            )
        ]
    )