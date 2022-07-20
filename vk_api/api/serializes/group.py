from marshmallow import Schema, fields, post_load
from dataclasses import dataclass


@dataclass
class InGroup:
    name: str
    id: int = None


@dataclass
class CreateGroup:
    name: str


class CreateGroupSchema(Schema):
    name = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return CreateGroup(**data)


class GroupSchema(Schema):
    id = fields.Int()
    name = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return InGroup(**data)


