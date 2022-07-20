from marshmallow import Schema, fields, post_load, post_dump
from vk_api.api.serializes.group import GroupSchema
from dataclasses import dataclass


@dataclass
class CreateUser:
    username: str
    password: str


@dataclass
class InBodyUser:
    username: str
    id: str


class UserSubSchema(Schema):
    id = fields.Int()
    username = fields.Str()

    @post_dump
    def convert_to_json(self, data, **kwargs):
        return InBodyUser(**data)


class UserSchema(Schema):
    username = fields.Str()
    password = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return CreateUser(**data)

    @post_dump
    def convert_to_json(self, data, **kwargs):
        del data["password"]
        return data


class UserGroupsSchema(Schema):
    username = fields.Str()
    groups = fields.Nested(GroupSchema(many=True))


class UserFollowerSchema(Schema):
    id = fields.Int()
    username = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return InBodyUser(**data)


class UserFollowersSchema(Schema):
    username = fields.Str()
    user_follower = fields.Nested(UserFollowerSchema(many=True))
    user_followed = fields.Nested(UserFollowerSchema(many=True))

