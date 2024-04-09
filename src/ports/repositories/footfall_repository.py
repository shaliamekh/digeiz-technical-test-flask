from abc import ABC, abstractmethod
from typing import Any

from domain.entities.footfall import Footfall


class FootfallRepository(ABC):
    @abstractmethod
    def add(self, footfall: Footfall) -> Footfall:
        pass

    @abstractmethod
    def get(self, **filters: Any) -> Footfall:
        pass

    @abstractmethod
    def delete(self, **filters: Any) -> None:
        pass

    @abstractmethod
    def update(self, fields_to_update: dict[str, Any], **filters: Any) -> None:
        pass

    @abstractmethod
    def get_all(self, **filters: Any) -> list[Footfall]:
        pass

    @abstractmethod
    def add_batch(self, footfalls: list[Footfall]) -> None:
        pass
