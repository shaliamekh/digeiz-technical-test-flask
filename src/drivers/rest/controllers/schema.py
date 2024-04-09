from dataclasses import asdict
from typing import Any

from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    post_load,
    validates_schema,
)
from marshmallow.validate import Length, Range

from domain.entities.footfall import Footfall, OriginType
from domain.entities.mall import Mall
from domain.entities.wall import Wall


class MallInput(Schema):
    name = fields.Str(required=True, validate=Length(min=3, max=60))

    @post_load
    def to_entity(self, data: dict[str, Any], **kwargs: Any) -> Mall:
        return Mall(**data)


class MallUpdate(Schema):
    name = fields.Str(validate=Length(min=3, max=60))


class MallResponse(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True, validate=Length(min=3, max=60))

    @classmethod
    def from_entity(cls, mall: Mall) -> Any:
        return cls().dump(asdict(mall))


class MallCollectionResponse(Schema):
    total_count = fields.Int(required=True)
    items = fields.Nested(MallResponse, many=True)

    @classmethod
    def from_entity(cls, malls: list[Mall], total_count: int) -> Any:
        return cls().dump(
            {"items": [asdict(mall) for mall in malls], "total_count": total_count}
        )


mall_collection_params = {
    "name_filter": fields.Str(),
    "limit": fields.Int(load_default=50),
    "page": fields.Int(load_default=1),
}


class WallInput(Schema):
    name = fields.Str(required=True, validate=Length(min=3, max=60))
    mall_id = fields.Int(required=True)

    @post_load
    def to_entity(self, data: dict[str, Any], **kwargs: Any) -> Wall:
        return Wall(**data)


class WallResponse(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True, validate=Length(min=3, max=60))
    mall = fields.Nested(MallResponse)

    class Meta:
        unknown = EXCLUDE

    @classmethod
    def from_entity(cls, wall: Wall) -> Any:
        return cls().dump(asdict(wall))


class WallCollectionResponse(Schema):
    total_count = fields.Int(required=True)
    items = fields.Nested(WallResponse, many=True)

    class Meta:
        unknown = EXCLUDE

    @classmethod
    def from_entity(cls, walls: list[Wall], total_count: int) -> Any:
        walls_dict = [asdict(wall) for wall in walls]
        return cls().dump({"items": walls_dict, "total_count": total_count})


wall_collection_params = {
    "name_filter": fields.Str(),
    "mall_id_filter": fields.Int(),
    "limit": fields.Int(load_default=50),
    "page": fields.Int(load_default=1),
}


class WallUpdate(Schema):
    name = fields.Str(validate=Length(min=3, max=60))


class FootfallInput(Schema):
    start_datetime = fields.DateTime(required=True)
    end_datetime = fields.DateTime(required=True)
    people_in = fields.Int(
        required=True, validate=Range(min=0, error="Value must not be lower than 0")
    )
    people_out = fields.Int(
        required=True, validate=Range(min=0, error="Value must not be lower than 0")
    )
    is_active = fields.Bool(load_default=True)
    origin = fields.Enum(OriginType, load_default=OriginType.raw)
    wall_id = fields.Int(required=True)

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data["start_datetime"] >= data["end_datetime"]:
            raise ValidationError(
                {
                    "datetime_fields": "start_datetime must not be later than end_datetime."
                }
            )

    @post_load
    def to_entity(self, data: dict[str, Any], **kwargs: Any) -> Footfall:
        return Footfall(**data)


class FootfallResponse(Schema):
    id = fields.Int(required=True)
    start_datetime = fields.DateTime(required=True)
    end_datetime = fields.DateTime(required=True)
    people_in = fields.Int(
        required=True, validate=Range(min=0, error="Value must not be lower than 0")
    )
    people_out = fields.Int(
        required=True, validate=Range(min=0, error="Value must not be lower than 0")
    )
    is_active = fields.Bool(required=True)
    origin = fields.Enum(OriginType, required=True)
    wall = fields.Nested(WallResponse)

    class Meta:
        unknown = EXCLUDE

    @classmethod
    def from_entity(cls, footfall: Footfall) -> Any:
        return cls().dump(asdict(footfall))


class FootfallCollectionResponse(Schema):
    total_count = fields.Int(required=True)
    items = fields.Nested(FootfallResponse, many=True)

    class Meta:
        unknown = EXCLUDE

    @classmethod
    def from_entity(cls, footfalls: list[Footfall], total_count: int) -> Any:
        footfalls_dict = [asdict(footfall) for footfall in footfalls]
        return cls().dump({"items": footfalls_dict, "total_count": total_count})


footfall_collection_params = {
    "is_active_filter": fields.Bool(),
    "wall_id_filter": fields.Int(),
    "origin_filter": fields.Enum(OriginType),
    "limit": fields.Int(load_default=50),
    "page": fields.Int(load_default=1),
}


class FootfallUpdate(Schema):
    is_active = fields.Bool()
    origin = fields.Enum(OriginType)
    start_datetime = fields.DateTime()
    end_datetime = fields.DateTime()
    people_in = fields.Int(
        validate=Range(min=0, error="Value must not be lower than 0")
    )
    people_out = fields.Int(
        validate=Range(min=0, error="Value must not be lower than 0")
    )


class FileSchema(Schema):
    file = fields.Raw(type="file")
