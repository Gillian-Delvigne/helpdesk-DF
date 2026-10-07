from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField
from app.forms.validators import TEXT_VALIDATORS, PASSWORD_VALIDATORS


class UserLoginForm(FlaskForm):
    name = StringField("Nom d'utilisateur", validators=TEXT_VALIDATORS)
    password = PasswordField("Mot de passe", validators=PASSWORD_VALIDATORS)
