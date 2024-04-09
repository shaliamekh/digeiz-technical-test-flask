from http import HTTPStatus
from typing import Any

from flask import g
from flask_apispec.views import MethodResource
from flask_restful import Resource

from adapters.repositories.wall_repository.sqlalchemy_repository import (
    SQLAlchemyWallRepository,
)
from domain.entities.wall import Wall
from drivers.rest.controllers.schema import (
    WallCollectionResponse,
    WallInput,
    WallResponse,
    WallUpdate,
    wall_collection_params,
)
from drivers.rest.utils.openapi import docs
from drivers.rest.utils.validation import validate_body, validate_int, validate_params


class WallController(MethodResource, Resource):
    @validate_body(WallInput)
    @docs(
        body_schema=WallInput,
        response_schema={HTTPStatus.OK: WallResponse},
        description="Create wall endpoint",
        tags=["Walls"],
    )
    def post(self, data: Wall):
        wall = SQLAlchemyWallRepository(g.session).add(data)
        return WallResponse.from_entity(wall=wall)

    @validate_params(wall_collection_params)
    @docs(
        params=wall_collection_params,
        response_schema={HTTPStatus.OK: WallCollectionResponse},
        description="List walls endpoint",
        tags=["Walls"],
    )
    def get(self, params: dict[str, Any]):
        repository = SQLAlchemyWallRepository(g.session)
        walls = repository.get_all(**params)
        count = repository.count(**params)
        return WallCollectionResponse.from_entity(walls, count)


class WallItemController(MethodResource, Resource):
    method_decorators = [validate_int]

    @docs(
        response_schema={HTTPStatus.OK: WallResponse},
        description="Get wall item endpoint",
        tags=["Walls"],
    )
    def get(self, wall_id: int):
        wall = SQLAlchemyWallRepository(g.session).get(id_filter=wall_id)
        return WallResponse.from_entity(wall)

    @validate_body(WallUpdate)
    @docs(
        body_schema=WallUpdate,
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Update wall item endpoint",
        tags=["Walls"],
    )
    def patch(self, wall_id: int, data: dict[str, Any]):
        SQLAlchemyWallRepository(g.session).update(
            fields_to_update=data, id_filter=wall_id
        )
        return "", 204

    @docs(
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Delete wall item endpoint",
        tags=["Walls"],
    )
    def delete(self, wall_id: int):
        SQLAlchemyWallRepository(g.session).delete(id_filter=wall_id)
        return "", 204
