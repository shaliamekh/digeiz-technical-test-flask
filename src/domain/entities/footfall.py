from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from domain.entities.wall import Wall


class OriginType(StrEnum):
    raw = "raw"
    reconstruction = "reconstruction"


@dataclass
class Footfall:
    start_datetime: datetime
    end_datetime: datetime
    people_in: int
    people_out: int
    is_active: bool
    origin: OriginType
    wall_id: int
    wall: Wall | None = None
    id: int | None = None
