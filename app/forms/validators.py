from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from app import app

DATA_REQUIRED_MSG = "Ce champ est requis"
LENGTH_MSG = "La longueur doit être comprise entre %(min)d et %(max)d caractères"

TEXT_VALIDATORS = [
    DataRequired(message=DATA_REQUIRED_MSG),
    Length(min=2, max=50, message=LENGTH_MSG),
]

TEXT_AREA_VALIDATORS = [
    DataRequired(message=DATA_REQUIRED_MSG),
    Length(min=2, max=500, message=LENGTH_MSG),
]

EMAIL_VALIDATORS = [
    DataRequired(message=DATA_REQUIRED_MSG),
    Email("L'adresse email est requise pour l'inscription"),
]

PASSWORD_VALIDATORS = (
    [
        DataRequired(message=DATA_REQUIRED_MSG),
        Length(
            4,
            25,
            message=LENGTH_MSG,
        ),
    ]
    if app.debug
    else [
        DataRequired(message=DATA_REQUIRED_MSG),
        Length(
            12,
            80,
            message=LENGTH_MSG,
        ),
        Regexp(
            r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!?(){}*$&@+=])",
            message="Le mot de passe doit contenir au moins une lettre minuscule, une majuscule, un chiffre et un caractère spécial : !?(){}*$&@+=",
        ),
    ]
)

PASSWORD_CONFIRM_VALIDATOR = EqualTo(
    "confirm", message="Les mots de passe encodés ne correspondent pas"
)
