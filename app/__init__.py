import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask import g
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# Load env variables contained in .env
load_dotenv()

app = Flask("app")

# Debug, ne pas laisser à True en production
app.debug = os.environ.get("DEBUG", "False").lower() in ("1", "true", "yes")

PLACEHOLDER_SECRET = "change-me"


def required_secret(name: str) -> str:
    """Lit un secret dans l'environnement, sans valeur de repli.

    Le placeholder versionné dans .env n'est toléré qu'en debug: hors debug,
    l'app refuse de démarrer plutôt que de signer avec une clé publique.
    """
    value = os.environ.get(name)
    if not value or (value == PLACEHOLDER_SECRET and not app.debug):
        raise RuntimeError(
            f"{name} doit être défini avec une valeur aléatoire: "
            "python -c \"import secrets; print(secrets.token_urlsafe(48))\""
        )
    return value


# La clé qui signe les cookies de session et les tokens CSRF.
app.config["SECRET_KEY"] = required_secret("SECRET_KEY")

# Les variables JWT pour encoder/decoder le token et assurer sa durée de vie
app.config["JWT_SECRET_KEY"] = required_secret("JWT_SECRET_KEY")
app.config["JWT_EXPIRES_IN"] = int(os.environ.get("JWT_EXPIRES_IN", "3600"))
app.config["JWT_COOKIE_NAME"] = "helpdesk_JWT"


# Ajoute un hook à l'envoi d'une réponse pour lui ajouter le cookie si nécessaire (login/logout)
@app.after_request
def set_cookie_with_JWT(response):
    if "request_type" in g:
        if g.request_type == "login" and "jwt" in g:
            response.set_cookie(
                app.config["JWT_COOKIE_NAME"],
                g.jwt,
                max_age=app.config["JWT_EXPIRES_IN"],
                httponly=True,
                secure=False,
                samesite="Lax",
            )
        elif g.request_type == "logout":
            response.delete_cookie(app.config["JWT_COOKIE_NAME"])
    return response


# Protection CSRF globale.
# FlaskForm valide déjà son jeton, mais CSRFProtect étend le contrôle à TOUTES
# les requêtes POST/PUT/DELETE, y compris celles qui n'ont pas de formulaire
# WTForms (nos boutons "supprimer", par exemple). Sans lui, ces routes seraient
# déclenchables depuis n'importe quel site tiers.
# Effet de bord pratique: la fonction csrf_token() devient disponible dans les
# templates.
csrf = CSRFProtect(app)

# Debug TOOLBAR
# INTERCEPT_REDIRECTS=False: sinon chaque redirection (et on en fait beaucoup
# en MVC, avec le motif POST -> redirect) affiche une page intermédiaire.
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

# SqlAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
# TRACK_MODIFICATIONS: système d'événements coûteux dont on ne se sert pas.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- 3) modèles et controllers ---------------------------------------------
# Ces deux imports en étoile chargent TOUS les fichiers des deux dossiers
# (voir le __all__ construit dynamiquement dans leurs __init__.py).
# Les modèles doivent être importés pour que SQLAlchemy connaisse les tables,
# les controllers pour que leurs @app.route s'enregistrent.
from app.models import *
from app.controllers import *

# --- 4) injection de dépendances -------------------------------------------
# L'import en étoile des services est ce qui remplit le catalogue: chaque classe
# décorée @injectable s'enregistre au moment où Python lit sa déclaration. Sans
# cet import, un service qu'aucun controller n'utilise directement (comme
# AuthServiceImpl) ne serait jamais enregistré.
# L'injecteur doit donc être créé APRÈS.
from app.services import *
from app.framework.injector import Injector

# On instancie ici (et pas dans main.py) pour que l'injecteur existe aussi quand
# l'app est lancée par `flask run` ou `flask db upgrade`.
injector = Injector(app)

# --- 5) seeds ---------------------------------------------------------------
# Même mécanisme une quatrième fois: l'import en étoile charge tous les fichiers
# de app/seed/, et chaque `class XxxSeed(Seedable)` s'enregistre à sa
# déclaration. Seed(app) n'a donc plus qu'à ajouter la route /seed — et
# uniquement si app.debug est vrai.
from app.seed import *
from app.framework.seed import Seed

seed = Seed(app)


# Injecte le current_user dans tous les templates via le context_processor pour bénéficier de l'information partout dans l'app
from app.framework.decorators.inject import inject
from app.services.auth_service import AbstractAuthService


@app.context_processor
@inject
def inject_current_user(auth_service: AbstractAuthService):
    return {"current_user": auth_service.get_current_user()}


@app.context_processor
def inject_dynamic_css_classes():
    return {
        "roletag_classes": {
            "CLIENT": {"bg": "bg-indigo-50", "border": "border-indigo-700"},
            "ADMIN": {
                "bg": "bg-red-50",
                "border": "border-red-700",
            },
            "TECHNICIEN": {
                "bg": "bg-orange-50",
                "border": "border-orange-700",
            },
        },
        "notification_classes": {
            "success": {
                "bg": "bg-green-50",
                "border": "border-green-700",
                "ring": "ring-green-500",
            },
            "warning": {
                "bg": "bg-yellow-50",
                "border": "border-yellow-700",
                "ring": "ring-yellow-500",
            },
            "error": {
                "bg": "bg-red-50",
                "border": "border-red-700",
                "ring": "ring-red-500",
            },
            "info": {
                "bg": "bg-blue-50",
                "border": "border-blue-700",
                "ring": "ring-blue-500",
            },
        },
    }
