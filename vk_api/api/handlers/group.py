import flask
from sqlalchemy.exc import IntegrityError
from vk_api.api.models.base import db
from vk_api.api.serializes.group import GroupSchema, ActionsGroupSchema
from vk_api.api.models.group import Group
from flask_restx import Resource, fields, Namespace
from vk_api.app.swagger import create_group
from vk_api.api.security.base import token_required, current_user
from vk_api.app.error.error import make_error

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
        params = ActionsGroupSchema().load(flask.request.json)
        new_group = Group(name=params.name)
        try:
            db.session.add(new_group)
            db.session.commit()
        except IntegrityError as e:
            if e.orig.pgcode in ['23505']:
                return make_error(status_code=406, message="Группа уже существует")
        return flask.jsonify(GroupSchema().dump(new_group))
