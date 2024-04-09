from typing import Callable

import pytest

from adapters.exceptions import MallNotFoundException, WallNotFoundException
from adapters.repositories.mall_repository.sqlalchemy_repository import (
    SQLAlchemyMallRepository,
)
from adapters.repositories.wall_repository.sqlalchemy_repository import (
    SQLAlchemyWallRepository,
)
from domain.entities.mall import Mall
from domain.entities.wall import Wall


@pytest.fixture(name="create_wall")
def create_wall_fixture(
    wall_repository: SQLAlchemyWallRepository, mall_repository: SQLAlchemyMallRepository
):
    def inner(name: str = "Test Wall"):
        mall = mall_repository.add(Mall(name="Test Mall"))
        assert mall.id
        return wall_repository.add(Wall(name=name, mall_id=mall.id, mall=mall))

    return inner


def test_add_wall_mall_not_found(wall_repository: SQLAlchemyWallRepository):
    wall = Wall(name="Test Mall", mall_id=555)
    with pytest.raises(MallNotFoundException):
        wall_repository.add(wall)


def test_add_get_wall(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    wall = create_wall()
    assert wall_repository.get(id_filter=wall.id) == wall


def test_get_wall_not_found(wall_repository: SQLAlchemyWallRepository):
    with pytest.raises(WallNotFoundException):
        assert wall_repository.get(id_filter=555)


def test_update_wall(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    wall = create_wall()
    fields_to_update = {"name": "New Wall"}
    wall_repository.update(fields_to_update, id_filter=wall.id)
    updated_wall = wall_repository.get(id_filter=wall.id)
    assert updated_wall is not None and updated_wall.name == fields_to_update["name"]


def test_update_wall_not_found(wall_repository: SQLAlchemyWallRepository):
    fields_to_update = {"name": "New Wall"}
    with pytest.raises(WallNotFoundException):
        wall_repository.update(fields_to_update, id_filter=555)


def test_delete_wall(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    wall = create_wall()
    wall_repository.delete(id_filter=wall.id)
    with pytest.raises(WallNotFoundException):
        assert wall_repository.get(id_filter=wall.id)


def test_get_all_walls(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    wall_1 = create_wall(name="Test Wall 1")
    wall_2 = create_wall(name="Test Wall 2")
    walls = wall_repository.get_all()
    assert len(walls) == 2
    assert wall_1 in walls and wall_2 in walls


def test_get_all_walls_with_name_filters(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    create_wall(name="Test Wall 1")
    create_wall(name="Test Wall 2")
    wall_3 = create_wall(name="Another Wall")
    walls = wall_repository.get_all(name_filter="Test Wall")
    assert len(walls) == 2
    assert wall_3 not in walls


def test_get_all_walls_with_pagination(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    create_wall(name="Test Wall 1")
    create_wall(name="Test Wall 2")
    create_wall(name="Another Wall")
    assert len(wall_repository.get_all(limit=2, page=1)) == 2


def test_get_all_walls_with_mall_id_filters(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    wall_1 = create_wall(name="Test Wall 1")
    wall_repository.add(Wall(name="Test Wall 2", mall_id=wall_1.mall_id))
    wall_3 = create_wall(name="Another Wall")
    walls = wall_repository.get_all(mall_id_filter=wall_1.mall_id)
    assert len(walls) == 2
    assert wall_3 not in walls


def test_count_walls(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    create_wall(name="Test Wall 1")
    create_wall(name="Test Wall 2")
    assert wall_repository.count() == 2


def test_count_walls_not_found(wall_repository: SQLAlchemyWallRepository):
    assert wall_repository.count() == 0


def test_count_walls_with_name_filters(
    wall_repository: SQLAlchemyWallRepository, create_wall: Callable[..., Wall]
):
    create_wall(name="Test Wall 1")
    create_wall(name="Test Wall 2")
    create_wall(name="Another Wall")
    assert wall_repository.count(name_filter="Test Wall") == 2
