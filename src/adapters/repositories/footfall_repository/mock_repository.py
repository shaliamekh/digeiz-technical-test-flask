import logging
from datetime import datetime
from typing import Any

from domain.entities.footfall import Footfall, OriginType
from ports.repositories.footfall_repository import FootfallRepository

logger = logging.getLogger()


class MockFootfallRepository(FootfallRepository):
    footfall = Footfall(
        start_datetime=datetime.now(),
        end_datetime=datetime.now(),
        people_in=100,
        people_out=90,
        is_active=True,
        origin=OriginType.raw,
        wall_id=1,
    )

    def add(self, footfall: Footfall) -> Footfall:
        return footfall

    def get(self, **filters: Any) -> Footfall:
        return self.footfall

    def update(self, fields_to_update: dict[str, Any], **filters: Any) -> None:
        return None

    def delete(self, **filters: Any) -> None:
        return None

    def get_all(self, page: int = 1, limit: int = 50, **filters: Any) -> list[Footfall]:
        return [self.footfall]

    def count(self, **filters: Any) -> int:
        return 1

    def add_batch(self, footfalls: list[Footfall]) -> None:
        return None
