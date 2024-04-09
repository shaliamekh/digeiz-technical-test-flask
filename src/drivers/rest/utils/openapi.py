import functools
from http import HTTPStatus
from typing import Any, Callable, ParamSpec, Type, TypeVar

from flask_apispec import doc, marshal_with, use_kwargs
from marshmallow import Schema

Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


def docs(
    *,
    response_schema: dict[HTTPStatus, Type[Schema] | dict[int, Any]],
    params: dict[str, Any] | None = None,
    body_schema: Type[Schema] | None = None,
    file_upload: Type[Schema] | None = None,
    description: str = "",
    tags: list[str] | None = None,
) -> Callable[..., Any]:
    def decorator(fn: Callable[Params, ReturnType]) -> Callable[Params, ReturnType]:
        doc_decorated = doc(description=description, tags=tags or [])(fn)
        for status, schema in response_schema.items():
            doc_decorated = marshal_with(
                schema=schema, code=status, description=status.name, apply=False
            )(doc_decorated)

        if params:
            doc_decorated = use_kwargs(params, location="query", apply=False)(
                doc_decorated
            )
        if body_schema:
            doc_decorated = use_kwargs(body_schema, location="json", apply=False)(
                doc_decorated
            )
        if file_upload:
            doc_decorated = use_kwargs(file_upload, location="files", apply=False)(
                doc_decorated
            )

        @functools.wraps(fn)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> Any:
            return doc_decorated(*args, **kwargs)

        return wrapper

    return decorator
