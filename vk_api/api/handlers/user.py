import flask
from flask_restx import Resource, Namespace
from vk_api.api.models.base import db
from vk_api.api.serializes.user import (
    UserGroupsSchema, UserSubSchema, UserFollowerSchema, UserFollowersSchema
)
from vk_api.api.serializes.group import GroupSchema
from vk_api.api.models.user import User, users_groups
from vk_api.api.models.group import Group
from vk_api.app.error.error import make_error
from vk_api.app.swagger import user_group, group, user_subscribe
from vk_api.api.security.base import token_required, current_user

api_user = Namespace('api/user', description='Функции пользователя')


@api_user.route('/')
class InfoUser(Resource):
    @api_user.doc(security="apiKey")
    @token_required
    def get(self):
        """
        Получить текущего пользователя.
        """
        return flask.jsonify(UserSubSchema().dump(current_user))


@api_user.route('/<int:user_id>/group/followed')
class UserGroupFollower(Resource):
    @api_user.doc(security="apiKey", model=user_group)
    @api_user.param('name', 'Введите подстроку названия группы')
    @token_required
    def get(self, user_id):
        """
        Найти группы у пользователя и его подписчиков.
        :param user_id: Какой-то id пользователя
        """
        _user = User.query.filter_by(id=user_id).first_or_404()
        id_follower = _user.list_identify_follower()
        params = flask.request.args
        if params:
            exp = params["name"]
            groups = Group.query.join(Group.user_groups).filter(User.id.in_(id_follower)).filter(
                Group.name.ilike(f"%{exp}%")).all()

            _user.groups = groups
        else:
            groups = Group.query.join(Group.user_groups).filter(User.id.in_(id_follower)).all()
            _user.groups = groups
        return flask.jsonify(UserGroupsSchema().dump(_user))


@api_user.route('/<int:user_id>/group')
class UserGroup(Resource):
    @api_user.doc(security="apiKey", model=user_group)
    @api_user.param('name', 'Введите подстроку названия группы')
    @token_required
    def get(self, user_id):
        """
        Получить или найти группы пользователя.
        :param user_id: Какой-то id пользователя
        """
        _user = User.query.filter_by(id=user_id).first_or_404()
        if flask.request.args:
            exp = flask.request.args["name"]
            groups = Group.query.join(Group.user_groups).filter(
                User.id == _user.id).filter(Group.name.ilike(f"%{exp}%")).all()

            _user.groups = groups

        return flask.jsonify(UserGroupsSchema().dump(_user))

    @api_user.doc(security="apiKey")
    @api_user.expect(group)
    @token_required
    def post(self, user_id: int):
        """
        Подписаться на группу.
        :param user_id: Ваш id пользователя
        """
        if user_id != current_user.id:
            return make_error(status_code=403, message="Вы не можете")

        payload = GroupSchema().load(flask.request.json)
        _group = Group.query.filter_by(id=payload.id).first_or_404()
        users_group = current_user.group_follow(_group)
        if users_group:
            db.session.add(users_group)
            db.session.commit()

            return flask.jsonify(UserGroupsSchema().dump(current_user))
        else:
            return make_error(status_code=208, message="Уже подписан")


@api_user.route('/<int:user_id>/user')
class SubscribeUser(Resource):
    @api_user.doc(security="apiKey")
    def get(self, user_id):
        """
        Получить подписки и подписчиков пользователя.
        :param user_id: Какой-то id пользователя
        """
        user_follower = User.query.filter_by(id=user_id).first_or_404()
        return flask.jsonify(UserFollowersSchema().dump(user_follower))

    @api_user.doc(security="apiKey")
    @api_user.expect(user_subscribe)
    @token_required
    def post(self, user_id: int):
        """
        Подписаться на пользователя.
        :param user_id: Ваш id пользователя
        """
        if user_id != current_user.id:
            return make_error(status_code=403, message="Вы не можете")

        payload = UserFollowerSchema().load(flask.request.json)
        user_follower = User.query.filter_by(id=payload.id).first_or_404()

        users = user_follower.user_follow(current_user)
        if users:
            db.session.add(users)
            db.session.commit()

            return flask.jsonify(UserFollowersSchema().dump(current_user))

        return make_error(status_code=208, message="Уже подписан")
