from marshmallow import Schema, fields, post_load
from dataclasses import dataclass


@dataclass
class InGroup:
    name: str
    id: int = None


@dataclass
class FollowGroup:
    id: int


@dataclass
class ActionsGroup:
    name: str


class ActionsGroupSchema(Schema):
    name = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return ActionsGroup(**data)


class FollowGroupSchema(Schema):
    id = fields.Int(data_key="group_id")

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return FollowGroup(**data)


class GroupSchema(Schema):
    id = fields.Int(data_key="group_id")
    name = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return InGroup(**data)


