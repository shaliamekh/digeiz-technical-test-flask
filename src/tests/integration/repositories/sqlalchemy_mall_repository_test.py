from typing import Callable

import pytest

from adapters.exceptions import MallNotFoundException
from adapters.repositories.mall_repository.sqlalchemy_repository import (
    SQLAlchemyMallRepository,
)
from domain.entities.mall import Mall


@pytest.fixture(name="create_mall")
def create_mall_fixture(mall_repository: SQLAlchemyMallRepository):
    def inner(name: str = "Test Mall"):
        return mall_repository.add(Mall(name=name))

    return inner


def test_add_get_mall(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    mall = create_mall()
    assert mall_repository.get(id_filter=mall.id) == mall


def test_get_mall_not_found(mall_repository: SQLAlchemyMallRepository):
    with pytest.raises(MallNotFoundException):
        mall_repository.get(id_filter=555)


def test_update_mall(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    mall = create_mall()
    fields_to_update = {"name": "New Mall"}
    mall_repository.update(fields_to_update, id_filter=mall.id)
    updated_mall = mall_repository.get(id_filter=mall.id)
    assert updated_mall is not None and updated_mall.name == fields_to_update["name"]


def test_update_mall_not_found(mall_repository: SQLAlchemyMallRepository):
    fields_to_update = {"name": "New Mall"}
    with pytest.raises(MallNotFoundException):
        mall_repository.update(fields_to_update, id_filter=555)


def test_delete_mall(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    mall = create_mall()
    mall_repository.delete(id_filter=mall.id)
    with pytest.raises(MallNotFoundException):
        mall_repository.get(id_filter=mall.id)


def test_delete_mall_not_found(mall_repository: SQLAlchemyMallRepository):
    with pytest.raises(MallNotFoundException):
        mall_repository.delete(id_filter=555)


def test_get_all_malls(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    mall_1 = create_mall(name="Test Mall 1")
    mall_2 = create_mall(name="Test Mall 2")
    malls = mall_repository.get_all()
    assert len(malls) == 2
    assert mall_1 in malls and mall_2 in malls


def test_get_all_malls_with_name_filters(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    create_mall(name="Test Mall 1")
    create_mall(name="Test Mall 2")
    mall_3 = create_mall(name="Another Mall")
    malls = mall_repository.get_all(name_filter="Test Mall")
    assert len(malls) == 2
    assert mall_3 not in malls


def test_get_all_malls_with_pagination(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    create_mall(name="Test Mall 1")
    create_mall(name="Test Mall 2")
    create_mall(name="Another Mall")
    assert len(mall_repository.get_all(limit=2, page=1)) == 2


def test_get_all_malls_not_found(mall_repository: SQLAlchemyMallRepository):
    malls = mall_repository.get_all()
    assert len(malls) == 0


def test_count_malls(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    create_mall(name="Test Mall 1")
    create_mall(name="Test Mall 2")
    assert mall_repository.count() == 2


def test_count_malls_not_found(mall_repository: SQLAlchemyMallRepository):
    assert mall_repository.count() == 0


def test_count_malls_with_name_filters(
    mall_repository: SQLAlchemyMallRepository, create_mall: Callable[..., Mall]
):
    create_mall(name="Test Mall 1")
    create_mall(name="Test Mall 2")
    create_mall(name="Another Mall")
    assert mall_repository.count(name_filter="Test Mall") == 2
