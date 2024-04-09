from dataclasses import dataclass

from domain.entities.mall import Mall


@dataclass
class Wall:
    name: str
    mall_id: int
    mall: Mall | None = None
    id: int | None = None
