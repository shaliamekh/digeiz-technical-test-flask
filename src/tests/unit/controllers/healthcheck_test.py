from http import HTTPStatus

from flask.testing import FlaskClient


def test_healthcheck(client: FlaskClient):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK
    assert response.json == {"status": "OK"}
