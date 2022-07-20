import flask
from vk_api.api.models.base import db
from vk_api.api.serializes.group import GroupSchema, CreateGroupSchema
from vk_api.api.models.group import Group
from flask_restx import Resource, fields, Namespace
from vk_api.app.swagger import create_group
from vk_api.api.security.base import token_required, current_user

api_group = Namespace('api/group', description='Создание и получение групп')


@api_group.route('/')
class Groups(Resource):
    @staticmethod
    def get():
        """
        Получить все доступные группы.
        """
        groups = Group.query.all()
        return flask.jsonify(GroupSchema(many=True).dump(groups))

    @api_group.doc(security="apiKey")
    @api_group.expect(create_group)
    @token_required
    def post(self):
        """
        Добавить группу.
        """
        params = CreateGroupSchema().load(flask.request.json)
        new_group = Group(name=params.name)
        db.session.add(new_group)
        db.session.commit()
        return flask.jsonify(GroupSchema().dump(new_group))
