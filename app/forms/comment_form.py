from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    """Création d'un commentaire.
    """

    comment_content =  TextAreaField(
        "Commentaire",
        validators=[
            DataRequired(message="Le contenu du commentaire est obligatoire !")
        ]
    )
