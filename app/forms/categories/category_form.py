from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


DATA_REQUIRED_MSG = "Field required!"
LENGTH_MSG = "Length must be between %(min)d and %(max)d characters"

class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""

    name = StringField(
        "Category Name",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            Length(min=2, max=100, message=LENGTH_MSG),
        ],
    )
    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            Length(
                min=2,
                max=255,
                message=LENGTH_MSG,
            ),
        ],
    )
    submit = SubmitField("Save")
