from abc import ABC, abstractmethod
from typing import Any

from domain.entities.wall import Wall


class WallRepository(ABC):
    @abstractmethod
    def add(self, wall: Wall) -> Wall:
        pass

    @abstractmethod
    def get(self, **filters: Any) -> Wall:
        pass

    @abstractmethod
    def delete(self, **filters: Any) -> None:
        pass

    @abstractmethod
    def update(self, fields_to_update: dict[str, Any], **filters: Any) -> None:
        pass

    @abstractmethod
    def get_all(self, **filters: Any) -> list[Wall]:
        pass
