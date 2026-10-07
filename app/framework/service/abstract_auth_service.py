from abc import ABC, abstractmethod

from app.dtos.user_dto import UserDTO


class AbstractAuthService(ABC):
    @abstractmethod
    def get_current_user(self) -> UserDTO | None:
        pass

    @abstractmethod
    def login(self, user: UserDTO) -> None:
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def is_authenticated(self) -> bool:
        pass
