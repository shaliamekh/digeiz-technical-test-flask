import functools
from typing import Any, Callable, ParamSpec, Type, TypeVar

from flask import request
from marshmallow import Schema, ValidationError
from marshmallow.fields import Field

Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


def validate_body(schema: Type[Schema]) -> Callable[..., Any]:
    def decorator(fn: Callable[Params, ReturnType]) -> Callable[Params, ReturnType]:
        @functools.wraps(fn)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
            model_body = schema()
            data = model_body.load(request.get_json())
            return fn(data=data, *args, **kwargs)

        return wrapper

    return decorator


def validate_params(params_mapping: dict[str, Field]) -> Callable[..., Any]:
    def decorator(fn: Callable[Params, ReturnType]) -> Callable[Params, ReturnType]:
        @functools.wraps(fn)
        def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
            schema = Schema.from_dict(
                {name: params_mapping.get(name) for name, value in request.args.items()}  # type: ignore
            )
            params = schema().load(request.args)
            return fn(params=params, *args, **kwargs)

        return wrapper

    return decorator


def validate_int(fn: Callable[Params, ReturnType]) -> Callable[Params, ReturnType]:
    @functools.wraps(fn)
    def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
        for key, value in kwargs.items():
            try:
                int(value)  # type: ignore
            except ValueError:
                raise ValidationError({key: ["Not a valid integer."]})
        return fn(*args, **kwargs)

    return wrapper
