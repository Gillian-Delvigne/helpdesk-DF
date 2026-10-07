from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField

from app.forms.validators import (
    TEXT_VALIDATORS,
    EMAIL_VALIDATORS,
    PASSWORD_VALIDATORS,
    PASSWORD_CONFIRM_VALIDATOR,
)


class UserRegisterForm(FlaskForm):
    name = StringField("Nom d'utilisateur", validators=TEXT_VALIDATORS)
    email = EmailField("Email", validators=EMAIL_VALIDATORS)
    password = PasswordField(
        "Mot de passe", validators=PASSWORD_VALIDATORS + [PASSWORD_CONFIRM_VALIDATOR]
    )
    confirm = PasswordField("Confirmation du mot de passe")
    firstname = StringField("Prénom", validators=TEXT_VALIDATORS)
    lastname = StringField("Nom de famille", validators=TEXT_VALIDATORS)
