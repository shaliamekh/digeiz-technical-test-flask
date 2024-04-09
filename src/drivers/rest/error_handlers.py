from http import HTTPStatus

from flask import Flask, Response, jsonify
from marshmallow import ValidationError

from adapters.exceptions import BaseNotFoundException, ExternalException
from use_cases.exceptions import NotValidFileException


def handle_errors(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_exception(exception: ValidationError) -> Response:
        response = jsonify({"details": exception.args})
        response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY
        return response

    @app.errorhandler(ExternalException)
    def handle_database_exception(exception: ExternalException) -> Response:
        response = jsonify({"details": "Something went wrong. Please try again later."})
        response.status_code = HTTPStatus.BAD_REQUEST
        return response

    @app.errorhandler(BaseNotFoundException)
    def handle_not_found_exception(exception: BaseNotFoundException) -> Response:
        response = jsonify({"details": str(exception)})
        response.status_code = HTTPStatus.NOT_FOUND
        return response

    @app.errorhandler(NotValidFileException)
    def handle_file_not_valid_exception(exception: NotValidFileException) -> Response:
        response = jsonify({"details": "The data is not valid."})
        response.status_code = HTTPStatus.UNPROCESSABLE_ENTITY
        return response
