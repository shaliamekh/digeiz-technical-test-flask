from http import HTTPStatus
from typing import Any

from flask import g
from flask_apispec.views import MethodResource
from flask_restful import Resource

from adapters.repositories.footfall_repository.sqlalchemy_repository import (
    SQLAlchemyFootfallRepository,
)
from domain.entities.footfall import Footfall
from drivers.rest.controllers.schema import (
    FootfallCollectionResponse,
    FootfallInput,
    FootfallResponse,
    FootfallUpdate,
    footfall_collection_params,
)
from drivers.rest.utils.openapi import docs
from drivers.rest.utils.validation import validate_body, validate_int, validate_params


class FootfallController(MethodResource, Resource):
    @validate_body(FootfallInput)
    @docs(
        body_schema=FootfallInput,
        response_schema={HTTPStatus.OK: FootfallResponse},
        description="Create footfall endpoint",
        tags=["Footfall"],
    )
    def post(self, data: Footfall):
        footfall = SQLAlchemyFootfallRepository(g.session).add(data)
        return FootfallResponse.from_entity(footfall=footfall)

    @validate_params(footfall_collection_params)
    @docs(
        params=footfall_collection_params,
        response_schema={HTTPStatus.OK: FootfallCollectionResponse},
        description="List footfall endpoint",
        tags=["Footfall"],
    )
    def get(self, params: dict[str, Any]):
        repository = SQLAlchemyFootfallRepository(g.session)
        walls = repository.get_all(**params)
        count = repository.count(**params)
        return FootfallCollectionResponse.from_entity(walls, count)


class FootfallItemController(MethodResource, Resource):
    method_decorators = [validate_int]

    @docs(
        response_schema={HTTPStatus.OK: FootfallResponse},
        description="Get footfall item endpoint",
        tags=["Footfall"],
    )
    def get(self, footfall_id: int):
        wall = SQLAlchemyFootfallRepository(g.session).get(id_filter=footfall_id)
        return FootfallResponse.from_entity(wall)

    @validate_body(FootfallUpdate)
    @docs(
        body_schema=FootfallUpdate,
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Update footfall item endpoint",
        tags=["Footfall"],
    )
    def patch(self, footfall_id: int, data: dict[str, Any]):
        SQLAlchemyFootfallRepository(g.session).update(
            fields_to_update=data, id_filter=footfall_id
        )
        return "", 204

    @docs(
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Delete footfall item endpoint",
        tags=["Footfall"],
    )
    def delete(self, footfall_id: int):
        SQLAlchemyFootfallRepository(g.session).delete(id_filter=footfall_id)
        return "", 204
