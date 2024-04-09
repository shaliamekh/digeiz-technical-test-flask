from datetime import datetime, timezone
from http import HTTPStatus

from flask.testing import FlaskClient

from adapters.exceptions import DatabaseException, FootfallNotFoundException
from adapters.repositories.footfall_repository.sqlalchemy_repository import (
    SQLAlchemyFootfallRepository,
)
from domain.entities.footfall import Footfall, OriginType
from domain.entities.mall import Mall
from domain.entities.wall import Wall
from drivers.rest.controllers.schema import FootfallCollectionResponse, FootfallResponse

PATH_PREFIX = "/api/footfalls"


def create_footfall() -> Footfall:
    mall = Mall(name="Test Mall", id=1)
    assert mall.id
    wall = Wall(name="Test Wall", mall_id=mall.id, mall=mall, id=1)
    assert wall.id
    return Footfall(
        start_datetime=datetime(
            year=2024, month=3, day=15, hour=8, tzinfo=timezone.utc
        ),
        end_datetime=datetime(year=2024, month=3, day=15, hour=9, tzinfo=timezone.utc),
        people_in=100,
        people_out=90,
        is_active=True,
        origin=OriginType.raw,
        wall_id=wall.id,
        wall=wall,
        id=1,
    )


def test_post_footfall_success(client: FlaskClient, monkeypatch):
    footfall = create_footfall()

    def mock_add(*args, **kwargs):
        return footfall

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "add", mock_add)
    payload = {
        "start_datetime": str(footfall.start_datetime),
        "end_datetime": str(footfall.end_datetime),
        "people_in": footfall.people_in,
        "people_out": footfall.people_out,
        "wall_id": footfall.wall_id,
    }
    response = client.post(PATH_PREFIX, json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json == FootfallResponse.from_entity(footfall)


def test_post_footfall_validation_error(client: FlaskClient):
    payload = {
        "start_datetime": "not_datetime",
        "end_datetime": "not_datetime",
        "people_in": -4,
        "people_out": -5,
        "wall_id": "not_uuid",
    }
    response = client.post(PATH_PREFIX, json=payload)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {
        "details": [
            {
                "end_datetime": ["Not a valid datetime."],
                "people_in": ["Value must not be lower than 0"],
                "people_out": ["Value must not be lower than 0"],
                "start_datetime": ["Not a valid datetime."],
                "wall_id": ["Not a valid integer."],
            }
        ]
    }


def test_post_footfall_database_error(client: FlaskClient, monkeypatch):
    def mock_add(*args, **kwargs):
        raise DatabaseException

    footfall = create_footfall()
    payload = {
        "start_datetime": str(footfall.start_datetime),
        "end_datetime": str(footfall.end_datetime),
        "people_in": footfall.people_in,
        "people_out": footfall.people_out,
        "wall_id": footfall.wall_id,
    }
    monkeypatch.setattr(SQLAlchemyFootfallRepository, "add", mock_add)
    response = client.post(PATH_PREFIX, json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json == {"details": "Something went wrong. Please try again later."}


def test_list_footfalls_success(client: FlaskClient, monkeypatch):
    footfalls = [
        create_footfall(),
        create_footfall(),
    ]

    def mock_get_all(*args, **kwargs):
        return footfalls

    def mock_count(*args, **kwargs):
        return len(footfalls)

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "get_all", mock_get_all)
    monkeypatch.setattr(SQLAlchemyFootfallRepository, "count", mock_count)
    response = client.get(PATH_PREFIX)
    assert response.status_code == HTTPStatus.OK
    assert response.json == FootfallCollectionResponse.from_entity(
        footfalls, len(footfalls)
    )


def test_list_footfalls_validation_error(client: FlaskClient):
    params = "page=df&limit=sdf&wall_id_filter=not_int&origin_filter=ds&is_active_filter=skdfh"
    response = client.get(f"{PATH_PREFIX}?{params}")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {
        "details": [
            {
                "is_active_filter": ["Not a valid boolean."],
                "limit": ["Not a valid integer."],
                "origin_filter": ["Must be one of: raw, reconstruction."],
                "page": ["Not a valid integer."],
                "wall_id_filter": ["Not a valid integer."],
            }
        ]
    }


def test_get_footfall_item_success(client: FlaskClient, monkeypatch):
    footfall = create_footfall()

    def mock_get(*args, **kwargs):
        return footfall

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "get", mock_get)
    response = client.get(f"{PATH_PREFIX}/{footfall.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json == FootfallResponse.from_entity(footfall)


def test_get_footfall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_get(*args, **kwargs):
        raise FootfallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "get", mock_get)
    response = client.get(f"{PATH_PREFIX}/{id_filter}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Footfall not found: id_filter={id_filter}"}


def test_get_footfall_item_validation_error(client: FlaskClient):
    response = client.get(f"{PATH_PREFIX}/not-valid-id")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"footfall_id": ["Not a valid integer."]}]}


def test_patch_footfall_item_success(client: FlaskClient, monkeypatch):
    def mock_update(*args, **kwargs):
        pass

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "update", mock_update)
    response = client.patch(
        f"{PATH_PREFIX}/{1}",
        json={"is_active": False, "origin": "reconstruction"},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_patch_footfall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_patch(*args, **kwargs):
        raise FootfallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "update", mock_patch)
    response = client.patch(
        f"{PATH_PREFIX}/{id_filter}",
        json={"is_active": False, "origin": "reconstruction"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Footfall not found: id_filter={id_filter}"}


def test_patch_footfall_item_validation_error(client: FlaskClient):
    response = client.patch(
        f"{PATH_PREFIX}/string_id",
        json={"is_active": False, "origin": "reconstruction"},
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"footfall_id": ["Not a valid integer."]}]}


def test_delete_footfall_item_success(client: FlaskClient, monkeypatch):
    def mock_delete(*args, **kwargs):
        pass

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "delete", mock_delete)
    response = client.delete(f"{PATH_PREFIX}/{1}")
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_footfall_item_not_found(client: FlaskClient, monkeypatch):
    id_filter = 1

    def mock_delete(*args, **kwargs):
        raise FootfallNotFoundException({"id_filter": id_filter})

    monkeypatch.setattr(SQLAlchemyFootfallRepository, "delete", mock_delete)
    response = client.delete(f"{PATH_PREFIX}/{id_filter}")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json == {"details": f"Footfall not found: id_filter={id_filter}"}


def test_delete_footfall_item_validation_error(client: FlaskClient):
    response = client.delete(f"{PATH_PREFIX}/string_id")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": [{"footfall_id": ["Not a valid integer."]}]}
