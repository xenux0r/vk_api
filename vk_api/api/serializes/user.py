from marshmallow import Schema, fields, post_load, post_dump
from vk_api.api.serializes.group import GroupSchema
from dataclasses import dataclass


@dataclass
class CreateUser:
    username: str
    password: str


@dataclass
class UserActions:
    id: str


class CreateUserSchema(Schema):
    username = fields.Str()
    password = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return CreateUser(**data)

    @post_dump
    def convert_security(self, data, **kwargs):
        del data["password"]
        return data


class UserGroupsSchema(Schema):
    username = fields.Str()
    groups = fields.Nested(GroupSchema(many=True))


class UserActionsSchema(Schema):
    id = fields.Int(data_key="user_id")
    username = fields.Str()

    @post_load
    def convert_to_dataclass(self, data, **kwargs):
        return UserActions(**data)


class UserActivitySchema(Schema):
    username = fields.Str()
    user_follower = fields.Nested(UserActionsSchema(many=True))
    user_followed = fields.Nested(UserActionsSchema(many=True))

