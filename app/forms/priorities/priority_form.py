from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


DATA_REQUIRED_MSG = "Field required!"
LENGTH_MSG = "Length must be between %(min)d and %(max)d characters"

class PriorityForm(FlaskForm):
    """Form for creating and editing priorities."""

    name = StringField(
        "Priority Name",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            Length(min=2, max=100, message=LENGTH_MSG),
        ],
    )
    level = IntegerField(
        "Priority Level",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            NumberRange(min=1, max=10, message="Must be between 1 and 10")
        ]
    )
    # 720 hours is about a month,
    # I chose this range arbitrarily and it can be discussed.
    delay_hours = IntegerField(
        "Delay Hours",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            NumberRange(min=1, max=720, message="Must be between 1 and 720")
        ]
    )
    submit = SubmitField("Save")