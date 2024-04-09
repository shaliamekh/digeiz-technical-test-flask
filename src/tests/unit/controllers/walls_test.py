from http import HTTPStatus

from flask.testing import FlaskClient

from adapters.exceptions import (
    DatabaseException,
    WallNotFoundException,
)
from adapters.repositories.wall_repository.sqlalchemy_repository import (
    SQLAlchemyWallRepository,
)
from domain.entities.wall import Wall
from drivers.rest.controllers.schema import (
    WallCollectionResponse,
    WallResponse,
)

PATH_PREFIX = "/api/walls"


def test_post_wall_success(client: FlaskClient, monkeypatch):
    wall = Wall(name="New Wall", id=1, mall_id=1)

    def mock_add(*args, **kwargs):
        return wall

    monkeypatch.setattr(SQLAlchemyWallRepository, "add", mock_add)
    response = client.post(
        PATH_PREFIX, json={"name": wall.name, "mall_id": wall.mall_id}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json == WallResponse.from_entity(wall)


def test_post_wall_validation_error(client: FlaskClient):
    response = client.post(PATH_PREFIX, json={"name": "So", "mall_id": "not_int"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {
        "details": [
            {
                "mall_id": ["Not a valid integer."],
                "name": ["Length must be between 3 and 60."],
            }
        ]
    }


def test_post_wall_database_error(client: FlaskClient, monkeypatch):
    def mock_add(*args, **kwargs):
        raise DatabaseException

    monkeypatch.setattr(SQLAlchemyWallRepository, "add", mock_add)
    response = client.post(PATH_PREFIX, json={"name": "New Wall", "mall_id": 1})
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {"details": "Something went wrong. Please try again later."}


def test_list_walls_success(client: FlaskClient, monkeypatch):
    walls = [
        Wall(name="New Wall", id=1, mall_id=1),
        Wall(name="Another Wall", id=2, mall_id=1),
    ]

    def mock_get_all(*args, **kwargs):
        return walls

    def mock_count(*args, **kwargs):
        return len(walls)

    monkeypatch.setattr(SQLAlchemyWallRepository, "get_all", mock_get_all)
    monkeypatch.setattr(SQLAlchemyWallRepository, "count", mock_count)
    response = client.get(PATH_PREFIX)
    assert response.status_code == HTTPStatus.OK
    assert response.json == WallCollectionResponse.from_entity(walls, len(walls))


def test_list_walls_validation_error(client: FlaskClient):
    response = client.get(
        f"{PATH_PREFIX}?page=string&limit=string&mall_id_filter=not_int"
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {
        "details": [
            {
                "limit": ["Not a valid integer."],
                "mall_id_filter": ["Not a valid integer."],
                "page": ["Not a valid integer."],
            }
        ]
    }


def test_get_wall_item_success(client: FlaskClient, monkeypatch):
    wall = Wall(name="New Wall", id=1, mall_id=1)

    def mock_get(*args, **kwargs):
        return wall

    monkeypatch.setattr(SQLAlchemyWallRepository, "get", mock_get)
    response = client.get(f"{PATH_PREFIX}/{wall.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json == WallResponse.from_entity(wall)


def test_get_wall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_get(*args, **kwargs):
        raise WallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyWallRepository, "get", mock_get)
    response = client.get(f"{PATH_PREFIX}/{id_filter}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Wall not found: id_filter={id_filter}"}


def test_get_wall_item_validation_error(client: FlaskClient):
    response = client.get(f"{PATH_PREFIX}/not-valid-id")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"wall_id": ["Not a valid integer."]}]}


def test_patch_wall_item_success(client: FlaskClient, monkeypatch):
    def mock_update(*args, **kwargs):
        pass

    monkeypatch.setattr(SQLAlchemyWallRepository, "update", mock_update)
    response = client.patch(f"{PATH_PREFIX}/1", json={"name": "Updated"})
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_patch_wall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_patch(*args, **kwargs):
        raise WallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyWallRepository, "update", mock_patch)
    response = client.patch(f"{PATH_PREFIX}/{id_filter}", json={"name": "Updated"})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Wall not found: id_filter={id_filter}"}


def test_patch_wall_item_validation_error(client: FlaskClient):
    response = client.patch(f"{PATH_PREFIX}/string_id", json={"name": "Updated"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"wall_id": ["Not a valid integer."]}]}


def test_delete_wall_item_success(client: FlaskClient, monkeypatch):
    def mock_delete(*args, **kwargs):
        pass

    monkeypatch.setattr(SQLAlchemyWallRepository, "delete", mock_delete)
    response = client.delete(f"{PATH_PREFIX}/1")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_wall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_delete(*args, **kwargs):
        raise WallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyWallRepository, "delete", mock_delete)
    response = client.delete(f"{PATH_PREFIX}/{id_filter}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Wall not found: id_filter={id_filter}"}


def test_delete_wall_item_validation_error(client: FlaskClient):
    response = client.delete(f"{PATH_PREFIX}/string_id")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"wall_id": ["Not a valid integer."]}]}
