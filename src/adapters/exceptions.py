from typing import Any


class ExternalException(Exception):
    pass


class DatabaseException(ExternalException):
    pass


class BaseNotFoundException(Exception):
    entity_name: str

    def __init__(self, filters: dict[str, Any]):
        self.filters = filters

    def __str__(self) -> str:
        filters = ""
        for key, value in self.filters.items():
            filters += f" {key}={value}"
        return f"{self.entity_name} not found:{filters}"


class MallNotFoundException(BaseNotFoundException):
    entity_name = "Mall"


class WallNotFoundException(BaseNotFoundException):
    entity_name = "Wall"


class FootfallNotFoundException(BaseNotFoundException):
    entity_name = "Footfall"
