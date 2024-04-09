from abc import ABC, abstractmethod
from typing import Any

from domain.entities.mall import Mall


class MallRepository(ABC):
    @abstractmethod
    def add(self, mall: Mall) -> Mall:
        pass

    @abstractmethod
    def get(self, **filters: Any) -> Mall:
        pass

    @abstractmethod
    def delete(self, **filters: Any) -> None:
        pass

    @abstractmethod
    def update(self, fields_to_update: dict[str, Any], **filters: Any) -> None:
        pass

    @abstractmethod
    def get_all(self, **filters: Any) -> list[Mall]:
        pass
