from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget
from app.forms.validators import TEXT_VALIDATORS, TEXT_AREA_VALIDATORS, Length


class SelectMultipleCheckboxesField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class TeamCreationForm(FlaskForm):
    name = StringField("Nom de l'équipe de support", validators=TEXT_VALIDATORS)
    description = TextAreaField("Description", validators=TEXT_AREA_VALIDATORS)
    members = SelectMultipleCheckboxesField(
        "Choisissez les membres de l'équipe",
        validators=[
            Length(min=1, message="Choississez au moins un technicien"),
        ],
        coerce=int,
        choices=[],
    )
