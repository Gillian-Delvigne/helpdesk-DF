from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

DATA_REQUIRED_MSG = "This field is required."
LENGTH_MSG = "Field must be between %(min)d and %(max)d characters."

class TicketForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            Length(min=2, max=100, message=LENGTH_MSG)
        ]
    )

    description = TextAreaField(
        "Description",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
            Length(min=2, max=500, message=LENGTH_MSG)
        ]
    )

    # - Categories, Priorities and Equipment choices are fetched
    #   and populated in the ticket_controller.py 
    # - Status will be set to "New" by default at creation
    #   in the ticket_controller.py

    category_id = SelectField(
        "Category",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
        ]
    )
    priority_id = SelectField(
        "Priority",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
        ]
    )

    equipment_id = SelectField(
        "Equipment",
        validators=[
            DataRequired(message=DATA_REQUIRED_MSG),
        ]
    )

    # - Author will be automatically set from the logged user
    #   in the ticket_service.py later. For now I just set id = 1 in ticket_service.py
    # - Due_Date is calculated in the ticket_service.py 
    #   from the creation date + the priority delay of the priority set.
    # - Technician is optional and will be set to None by default.

    submit = SubmitField("Save")
