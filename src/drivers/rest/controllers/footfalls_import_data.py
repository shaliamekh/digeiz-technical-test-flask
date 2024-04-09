from http import HTTPStatus
from io import BytesIO

from flask import g, request
from flask_apispec import MethodResource
from flask_restful import Resource

from adapters.repositories.footfall_repository.sqlalchemy_repository import (
    SQLAlchemyFootfallRepository,
)
from drivers.rest.controllers.schema import FileSchema
from drivers.rest.utils.openapi import docs
from use_cases.process_footfalls_use_case import ProcessFootfallsUseCase


class FootfallImportDataController(MethodResource, Resource):
    @docs(
        file_upload=FileSchema,
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Import footfalls from file",
        tags=["Footfall File Import"],
    )
    def post(self):
        file = request.files["file"]
        file_buffer = BytesIO(file.read())
        use_case = ProcessFootfallsUseCase(SQLAlchemyFootfallRepository(g.session))
        use_case(file_buffer)
        return "", 204
