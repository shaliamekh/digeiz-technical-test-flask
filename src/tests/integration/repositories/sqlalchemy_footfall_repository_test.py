from datetime import datetime, timedelta, timezone
from typing import Callable

import pytest

from adapters.exceptions import FootfallNotFoundException, WallNotFoundException
from adapters.repositories.footfall_repository.sqlalchemy_repository import (
    SQLAlchemyFootfallRepository,
)
from adapters.repositories.mall_repository.sqlalchemy_repository import (
    SQLAlchemyMallRepository,
)
from adapters.repositories.wall_repository.sqlalchemy_repository import (
    SQLAlchemyWallRepository,
)
from domain.entities.footfall import Footfall, OriginType
from domain.entities.mall import Mall
from domain.entities.wall import Wall


@pytest.fixture(name="create_footfall")
def create_footfall_fixture(
    footfall_repository: SQLAlchemyFootfallRepository,
    wall_repository: SQLAlchemyWallRepository,
    mall_repository: SQLAlchemyMallRepository,
):
    def inner(
        start_datetime: datetime = datetime(day=1, month=3, year=2024, hour=12),
        is_active: bool = True,
        origin: OriginType = OriginType.reconstruction,
    ):
        mall = mall_repository.add(Mall(name="Test Mall"))
        assert mall.id
        wall = wall_repository.add(Wall(name="Test Wall", mall_id=mall.id, mall=mall))
        assert wall and wall.id
        footfall = Footfall(
            start_datetime=start_datetime,
            end_datetime=start_datetime + timedelta(hours=1),
            people_in=100,
            people_out=90,
            is_active=is_active,
            origin=origin,
            wall_id=wall.id,
            wall=wall,
        )
        return footfall_repository.add(footfall)

    return inner


def test_add_footfall_wall_not_found(footfall_repository: SQLAlchemyFootfallRepository):
    dt = datetime(day=1, month=3, year=2024, hour=12)
    footfall = Footfall(
        start_datetime=dt,
        end_datetime=dt + timedelta(hours=1),
        people_in=100,
        people_out=90,
        is_active=True,
        origin=OriginType.reconstruction,
        wall_id=1,
    )
    with pytest.raises(WallNotFoundException):
        assert footfall_repository.add(footfall)


#
def test_add_get_footfall(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    footfall = create_footfall()
    assert footfall_repository.get(id_filter=footfall.id) == footfall


def test_get_footfall_not_found(footfall_repository: SQLAlchemyFootfallRepository):
    with pytest.raises(FootfallNotFoundException):
        footfall_repository.get(id_filter=55)


def test_update_footfall(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    footfall = create_footfall()
    fields_to_update = {"is_active": False, "origin": OriginType.raw}
    footfall_repository.update(fields_to_update, id_filter=footfall.id)
    updated_footfall = footfall_repository.get(id_filter=footfall.id)
    assert updated_footfall is not None
    assert updated_footfall.is_active is False
    assert updated_footfall.origin == OriginType.raw


def test_update_footfall_not_found(footfall_repository: SQLAlchemyFootfallRepository):
    fields_to_update = {"is_active": False, "origin": OriginType.raw}
    with pytest.raises(FootfallNotFoundException):
        footfall_repository.update(fields_to_update, id_filter=555)


def test_delete_footfall(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    footfall = create_footfall()
    footfall_repository.delete(id_filter=footfall.id)
    with pytest.raises(FootfallNotFoundException):
        footfall_repository.get(id_filter=footfall.id)


def test_delete_footfall_not_found(
    footfall_repository: SQLAlchemyFootfallRepository,
):
    with pytest.raises(FootfallNotFoundException):
        footfall_repository.delete(id_filter=555)


def test_get_all_footfalls(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    footfall_1 = create_footfall()
    footfall_2 = create_footfall()
    footfalls = footfall_repository.get_all()
    assert len(footfalls) == 2
    assert footfall_1 in footfalls and footfall_2 in footfalls


def test_get_all_footfalls_with_is_active_filters(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    create_footfall(is_active=True)
    create_footfall(is_active=True)
    create_footfall(is_active=False)
    assert len(footfall_repository.get_all(is_active_filter=True)) == 2
    assert len(footfall_repository.get_all(is_active_filter=False)) == 1


def test_get_all_footfalls_with_wall_id_filters(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    footfall_1 = create_footfall()
    footfall_2 = Footfall(
        start_datetime=datetime.now(tz=timezone.utc),
        end_datetime=datetime.now(tz=timezone.utc) + timedelta(hours=1),
        people_in=100,
        people_out=90,
        is_active=True,
        origin=OriginType.reconstruction,
        wall_id=footfall_1.wall_id,
    )
    footfall_repository.add(footfall_2)
    footfall_3 = create_footfall()
    footfalls = footfall_repository.get_all(wall_id_filter=footfall_1.wall_id)
    assert len(footfalls) == 2
    assert footfall_3 not in footfalls


def test_get_all_footfalls_with_origin_filters(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    create_footfall(origin=OriginType.reconstruction)
    create_footfall(origin=OriginType.reconstruction)
    create_footfall(origin=OriginType.raw)
    assert (
        len(footfall_repository.get_all(origin_filter=OriginType.reconstruction)) == 2
    )
    assert len(footfall_repository.get_all(origin_filter=OriginType.raw)) == 1


def test_get_all_footfalls_with_pagination(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    for _ in range(3):
        create_footfall()
    assert len(footfall_repository.get_all(limit=2, page=1)) == 2


def test_count_footfalls(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    create_footfall()
    create_footfall()
    assert footfall_repository.count() == 2


def test_count_footfalls_not_found(
    footfall_repository: SQLAlchemyFootfallRepository,
):
    assert footfall_repository.count() == 0


def test_count_footfalls_with_origin_filters(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    create_footfall(origin=OriginType.reconstruction)
    create_footfall(origin=OriginType.reconstruction)
    create_footfall(origin=OriginType.raw)
    assert footfall_repository.count(origin_filter=OriginType.reconstruction) == 2


def test_update_footfalls_between_dates(
    footfall_repository: SQLAlchemyFootfallRepository,
    create_footfall: Callable[..., Footfall],
):
    date1 = datetime(day=1, month=3, year=2024)
    footfall = create_footfall(start_datetime=date1)
    date2 = datetime(day=2, month=3, year=2024)
    footfall2 = Footfall(
        start_datetime=date2,
        end_datetime=date2 + timedelta(hours=1),
        people_in=100,
        people_out=90,
        is_active=True,
        origin=OriginType.reconstruction,
        wall_id=footfall.wall_id,
    )
    footfall2 = footfall_repository.add(footfall2)
    date3 = datetime(day=11, month=3, year=2024)
    footfall3 = Footfall(
        start_datetime=date3,
        end_datetime=date3 + timedelta(hours=1),
        people_in=100,
        people_out=90,
        is_active=True,
        origin=OriginType.reconstruction,
        wall_id=footfall.wall_id,
    )
    footfall3 = footfall_repository.add(footfall3)

    fields_to_update = {"is_active": False}

    footfall_repository.update(
        fields_to_update,
        wall_id_filter=footfall.wall_id,
        start_date_between_filter=(date1, date2),
    )

    assert footfall_repository.get(id_filter=footfall.id).is_active is False
    assert footfall_repository.get(id_filter=footfall2.id).is_active is False
    assert footfall_repository.get(id_filter=footfall3.id).is_active is True


def test_add_batch_footfalls(
    footfall_repository: SQLAlchemyFootfallRepository,
    mall_repository: SQLAlchemyMallRepository,
    wall_repository: SQLAlchemyWallRepository,
    create_footfall: Callable[..., Footfall],
):
    mall = mall_repository.add(Mall(name="Test Mall"))
    assert mall.id
    wall = wall_repository.add(Wall(name="Test Wall", mall_id=mall.id, mall=mall))
    assert wall and wall.id
    footfalls = []
    for _ in range(3):
        footfall = Footfall(
            start_datetime=datetime(day=1, month=3, year=2024),
            end_datetime=datetime(day=1, month=3, year=2024) + timedelta(hours=1),
            people_in=100,
            people_out=90,
            is_active=True,
            origin=OriginType.reconstruction,
            wall_id=wall.id,
        )
        footfalls.append(footfall)
    footfall_repository.add_batch(footfalls)
    assert footfall_repository.count() == len(footfalls)


def test_add_batch_footfalls_wall_not_found(
    footfall_repository: SQLAlchemyFootfallRepository,
):
    footfalls = []
    for _ in range(3):
        footfall = Footfall(
            start_datetime=datetime(day=1, month=3, year=2024),
            end_datetime=datetime(day=1, month=3, year=2024) + timedelta(hours=1),
            people_in=100,
            people_out=90,
            is_active=True,
            origin=OriginType.reconstruction,
            wall_id=55,
        )
        footfalls.append(footfall)
    with pytest.raises(WallNotFoundException):
        footfall_repository.add_batch(footfalls)
