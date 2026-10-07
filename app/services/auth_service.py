import jwt
from flask import g, request


from app.framework.service.abstract_auth_service import AbstractAuthService
from app.framework.decorators.injectable import injectable
from app.framework.decorators.inject import inject
from app.framework.injector import Scope

from app.dtos.user_dto import UserDTO
from app.services.user_service import UserService
from app import app


@injectable(base=AbstractAuthService, scope=Scope.SCOPED)
class AuthService(AbstractAuthService):
    @inject
    def __init__(self, user_service: UserService):
        self.__user_service = user_service

    def get_current_user(self) -> UserDTO | None:
        try:
            token = request.cookies.get(app.config["JWT_COOKIE_NAME"])
            if token is None:
                return None
            payload = jwt.decode(
                token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            user_id = payload["user_id"]
            return self.__user_service.find_one(user_id)
        except Exception as e:
            if isinstance(e, jwt.ExpiredSignatureError):
                app.logger.error(
                    f"Erreur lors de l'authentification (token expiré): {e}"
                )
            elif isinstance(e, jwt.InvalidTokenError):
                app.logger.error(
                    f"Erreur lors de l'authentification (signature invalide ou mal formatée): {e}"
                )
            else:
                app.logger.error(f"Erreur lors de l'authentification (indéfinie): {e}")

    def login(self, user: UserDTO) -> None:
        try:
            g.request_type = "login"
            g.jwt = jwt.encode(
                {"user_id": user.user_id},
                app.config["JWT_SECRET_KEY"],
                algorithm="HS256",
            )
        except Exception as e:
            app.logger.error(f"Erreur lors de l'authentification (login): {e}")

    def logout(self):
        try:
            g.request_type = "logout"
        except Exception as e:
            app.logger.error(f"Erreur lors de l'authentification (logout): {e}")

    def is_authenticated(self) -> bool:
        return self.get_current_user() is not None
