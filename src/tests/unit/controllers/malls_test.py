from http import HTTPStatus

from flask.testing import FlaskClient

from adapters.exceptions import DatabaseException, MallNotFoundException
from adapters.repositories.mall_repository.sqlalchemy_repository import (
    SQLAlchemyMallRepository,
)
from domain.entities.mall import Mall
from drivers.rest.controllers.schema import MallCollectionResponse, MallResponse

PATH_PREFIX = "/api/malls"


def test_post_mall_success(client: FlaskClient, monkeypatch):
    mall = Mall(name="New Mall", id=1)

    def mock_add(*args, **kwargs):
        return mall

    monkeypatch.setattr(SQLAlchemyMallRepository, "add", mock_add)
    response = client.post(PATH_PREFIX, json={"name": mall.name})
    assert response.status_code == HTTPStatus.OK
    assert response.json == MallResponse.from_entity(mall)


def test_post_mall_validation_error(client: FlaskClient):
    response = client.post(PATH_PREFIX, json={"name": "So"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    expected = {"details": [{"name": ["Length must be between 3 and 60."]}]}
    assert response.json == expected


def test_post_mall_database_error(client: FlaskClient, monkeypatch):
    def mock_add(*args, **kwargs):
        raise DatabaseException

    monkeypatch.setattr(SQLAlchemyMallRepository, "add", mock_add)
    response = client.post(PATH_PREFIX, json={"name": "New Mall"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {"details": "Something went wrong. Please try again later."}


def test_list_malls_success(client: FlaskClient, monkeypatch):
    malls = [
        Mall(name="New Mall", id=1),
        Mall(name="Another Mall", id=2),
    ]

    def mock_get_all(*args, **kwargs):
        return malls

    def mock_count(*args, **kwargs):
        return len(malls)

    monkeypatch.setattr(SQLAlchemyMallRepository, "get_all", mock_get_all)
    monkeypatch.setattr(SQLAlchemyMallRepository, "count", mock_count)
    response = client.get(PATH_PREFIX)
    assert response.status_code == HTTPStatus.OK
    assert response.json == MallCollectionResponse.from_entity(malls, len(malls))


def test_list_malls_validation_error(client: FlaskClient):
    response = client.get(f"{PATH_PREFIX}?page=string&limit=string")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    errors = {"limit": ["Not a valid integer."], "page": ["Not a valid integer."]}
    assert response.json == {"details": [errors]}


def test_get_mall_item_success(client: FlaskClient, monkeypatch):
    mall = Mall(name="Test Mall", id=1)

    def mock_get(*args, **kwargs):
        return mall

    monkeypatch.setattr(SQLAlchemyMallRepository, "get", mock_get)
    response = client.get(f"{PATH_PREFIX}/{mall.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json == MallResponse.from_entity(mall)


def test_get_mall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_get(*args, **kwargs):
        raise MallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyMallRepository, "get", mock_get)
    response = client.get(f"{PATH_PREFIX}/{id_filter}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Mall not found: id_filter={id_filter}"}


def test_get_mall_item_validation_error(client: FlaskClient):
    response = client.get(f"{PATH_PREFIX}/not-valid-id")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"mall_id": ["Not a valid integer."]}]}


def test_patch_mall_item_success(client: FlaskClient, monkeypatch):
    def mock_update(*args, **kwargs):
        pass

    monkeypatch.setattr(SQLAlchemyMallRepository, "update", mock_update)
    response = client.patch(f"{PATH_PREFIX}/{1}", json={"name": "Updated"})
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_patch_mall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 55

    def mock_patch(*args, **kwargs):
        raise MallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyMallRepository, "update", mock_patch)
    response = client.patch(f"{PATH_PREFIX}/{id_filter}", json={"name": "Updated"})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Mall not found: id_filter={id_filter}"}


def test_patch_mall_item_validation_error(client: FlaskClient):
    response = client.patch(f"{PATH_PREFIX}/string_id", json={"name": "Updated"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"mall_id": ["Not a valid integer."]}]}


def test_delete_mall_item_success(client: FlaskClient, monkeypatch):
    def mock_delete(*args, **kwargs):
        pass

    monkeypatch.setattr(SQLAlchemyMallRepository, "delete", mock_delete)
    response = client.delete(f"{PATH_PREFIX}/{1}")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_mall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_delete(*args, **kwargs):
        raise MallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyMallRepository, "delete", mock_delete)
    response = client.delete(f"{PATH_PREFIX}/{id_filter}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Mall not found: id_filter={id_filter}"}


def test_delete_mall_item_validation_error(client: FlaskClient):
    response = client.delete(f"{PATH_PREFIX}/string_id")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"mall_id": ["Not a valid integer."]}]}
