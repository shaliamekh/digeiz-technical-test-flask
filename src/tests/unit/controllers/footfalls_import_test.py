from http import HTTPStatus
from io import BytesIO

from flask.testing import FlaskClient

from use_cases.exceptions import NotValidFileException
from use_cases.process_footfalls_use_case import ProcessFootfallsUseCase

PATH_PREFIX = "/api/footfalls/import-data"


def test_post_footfall_success(client: FlaskClient, monkeypatch):
    def mock_call(*args, **kwargs):
        pass

    monkeypatch.setattr(ProcessFootfallsUseCase, "__call__", mock_call)

    data = {"file": (BytesIO(b"test data"), "file")}
    response = client.post(
        PATH_PREFIX,
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_post_footfall_file_not_valid(client: FlaskClient, monkeypatch):
    def mock_call(*args, **kwargs):
        raise NotValidFileException

    monkeypatch.setattr(ProcessFootfallsUseCase, "__call__", mock_call)

    data = {"file": (BytesIO(b"test data"), "file")}
    response = client.post(
        PATH_PREFIX,
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json == {"details": "The data is not valid."}
