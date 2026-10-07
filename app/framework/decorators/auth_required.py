from flask import redirect, request, url_for, abort, flash
from functools import wraps
from app import app


def auth_required(role_name=None, is_current_user=False):
    """
    Usage du décorateur:
    A apposer à toute route dans les différents controllers qui nécessite a minima d'être authentifié (login).
    1) L'admin est toujours autorisé : on vérifie cela dans les role de l'utilisateur par défaut.
    2) Sans paramètre : role_name=None et is_current_user=False : route protégée par authentification pour un utilisateur lambda (login attendu). L'admin passe.
    3) Avec un role_name="autre_role_valide", la route autorise les utilisateurs possédant ce rôle (ex. Technicien)
    4) Avec un is_current_user à True, la route autorise l'utilisateur qui effectue la requête (et non les autres). Ex. L'auteur d'un commentaire peut éditer son propre commentaire, mais pas ceux des autres clients.
    (Ne pas oublier les parenthèses : @auth_required() car on est sur un décorateur à deux niveaux qui peut prendre des paramètres.)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_service = app.injector["AbstractAuthService"]
            current_user = auth_service.get_current_user()

            if current_user is None:
                flash("Vous devez être connecté pour accéder à cette page.", "warning")
                return redirect(url_for("login", next=request.path))
            if current_user.is_admin():
                return func(*args, **kwargs)
            if role_name is not None and current_user.has_role(role_name):
                return func(*args, **kwargs)
            if is_current_user and current_user.user_id == kwargs.get("user_id"):
                return func(*args, **kwargs)
            if not role_name and not is_current_user:
                return func(*args, **kwargs)
            abort(403)

        return wrapper

    return decorator
