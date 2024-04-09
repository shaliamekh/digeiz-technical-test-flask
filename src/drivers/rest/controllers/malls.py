from http import HTTPStatus
from typing import Any

from flask import g
from flask_apispec.views import MethodResource
from flask_restful import Resource

from adapters.repositories.mall_repository.sqlalchemy_repository import (
    SQLAlchemyMallRepository,
)
from domain.entities.mall import Mall
from drivers.rest.controllers.schema import (
    MallCollectionResponse,
    MallInput,
    MallResponse,
    MallUpdate,
    mall_collection_params,
)
from drivers.rest.utils.openapi import docs
from drivers.rest.utils.validation import validate_body, validate_int, validate_params


class MallController(MethodResource):
    @validate_body(MallInput)
    @docs(
        body_schema=MallInput,
        response_schema={HTTPStatus.OK: MallResponse},
        description="Create mall endpoint",
        tags=["Malls"],
    )
    def post(self, data: Mall):
        mall = SQLAlchemyMallRepository(g.session).add(data)
        return MallResponse.from_entity(mall=mall)

    @docs(
        params=mall_collection_params,
        response_schema={HTTPStatus.OK: MallCollectionResponse},
        description="List malls endpoint",
        tags=["Malls"],
    )
    @validate_params(mall_collection_params)
    def get(self, params: dict[str, Any]):
        repository = SQLAlchemyMallRepository(g.session)
        malls = repository.get_all(**params)
        count = repository.count(**params)
        return MallCollectionResponse.from_entity(malls, count)


class MallItemController(MethodResource, Resource):
    method_decorators = [validate_int]

    @docs(
        response_schema={HTTPStatus.OK: MallResponse},
        description="Get mall item endpoint",
        tags=["Malls"],
    )
    def get(self, mall_id: int):
        mall = SQLAlchemyMallRepository(g.session).get(id_filter=mall_id)
        return MallResponse.from_entity(mall)

    @validate_body(MallUpdate)
    @docs(
        body_schema=MallUpdate,
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Update mall item endpoint",
        tags=["Malls"],
    )
    def patch(self, mall_id: int, data: dict[str, Any]):
        SQLAlchemyMallRepository(g.session).update(
            fields_to_update=data, id_filter=mall_id
        )
        return "", 204

    @docs(
        response_schema={HTTPStatus.NO_CONTENT: {}},
        description="Delete mall item endpoint",
        tags=["Malls"],
    )
    def delete(self, mall_id: int):
        SQLAlchemyMallRepository(g.session).delete(id_filter=mall_id)
        return "", 204
