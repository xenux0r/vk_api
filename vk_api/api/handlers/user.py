import typing as t
import flask
from flask_restx import Resource, Namespace
from vk_api.api.models.base import db
from vk_api.api.serializes.user import (
    UserGroupsSchema, UserActionsSchema, UserActivitySchema, UserActions
)
from vk_api.api.serializes.group import ActionsGroupSchema, ActionsGroup, FollowGroup
from vk_api.api.serializes.group import FollowGroupSchema
from vk_api.api.models.user import User
from vk_api.api.models.group import Group
from vk_api.app.error.error import make_error
from vk_api.app.swagger import user_group, group, user_actions
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
        return flask.jsonify(UserActionsSchema().dump(current_user))


@api_user.route('/follow')
class UserFollow(Resource):
    @api_user.doc(security="apiKey")
    @api_user.expect(user_actions)
    @token_required
    def post(self):
        """
        Подписаться на пользователя.
        """
        payload: UserActions = UserActionsSchema().load(flask.request.json)
        user: User = User.query.filter_by(id=payload.id).first_or_404(description="Пользователь не найден")

        users: User = user.user_follow(current_user)
        if users:
            db.session.add(users)
            db.session.commit()

            return flask.jsonify(UserActivitySchema().dump(current_user))

        return make_error(status_code=208, message="Уже подписан")


@api_user.route('/group')
class UserGroup(Resource):
    @api_user.doc(security="apiKey", model=user_group)
    @api_user.param('name', 'Введите подстроку названия группы')
    @token_required
    def get(self):
        """
        Получить или найти группы у текущего пользователя.
        """
        params = flask.request.args
        if params:
            exp: ActionsGroup = ActionsGroupSchema().load(params)
            groups = Group.query.join(Group.user_groups).filter(
                User.id == current_user.id).filter(
                Group.name.ilike(f"%{exp.name}%")).all()
            current_user.groups = groups

        return flask.jsonify(UserGroupsSchema().dump(current_user))

    @api_user.doc(security="apiKey")
    @api_user.expect(group)
    @token_required
    def post(self):
        """
        Подписаться на группу.
        :param user_id: Ваш id пользователя
        """
        payload: FollowGroup = FollowGroupSchema().load(flask.request.json)
        _group: Group = Group.query.filter_by(id=payload.id).first_or_404(description="Группа не найдена")
        users_group: User = current_user.group_follow(_group)
        if users_group:
            db.session.add(users_group)
            db.session.commit()

            return flask.jsonify(UserGroupsSchema().dump(current_user))
        else:
            return make_error(status_code=208, message="Уже подписан")


@api_user.route('/<int:user_id>/group/follow')
class UserFollowGroup(Resource):
    @api_user.doc(security="apiKey", model=user_group)
    @api_user.param('name', 'Введите подстроку названия группы')
    @token_required
    def get(self, user_id):
        """
        Найти группы у пользователя и его подписчиков.
        :param user_id: Какой-то id пользователя
        """
        _user: User = User.query.filter_by(id=user_id).first_or_404(description="Пользователь не найден")
        id_follower: t.List = _user.list_identify_follower()
        params = flask.request.args
        if params:
            exp: ActionsGroup = ActionsGroupSchema().load(params)
            groups: Group = Group.query.join(Group.user_groups).filter(User.id.in_(id_follower)).filter(
                Group.name.ilike(f"%{exp.name}%")).all()

            _user.groups = groups
        else:
            groups: Group = Group.query.join(Group.user_groups).filter(User.id.in_(id_follower)).all()
            _user.groups = groups
        return flask.jsonify(UserGroupsSchema().dump(_user))


@api_user.route('/<int:user_id>/group')
class AllUsersGroup(Resource):
    @api_user.doc(security="apiKey", model=user_group)
    @api_user.param('name', 'Введите подстроку названия группы')
    @token_required
    def get(self, user_id):
        """
        Получить или найти группы конкретного пользователя.
        :param user_id: Какой-то id пользователя
        """
        _user: User = User.query.filter_by(id=user_id).first_or_404(description="Пользователь не найден")
        params = flask.request.args
        if params:
            exp: ActionsGroup = ActionsGroupSchema().load(params)
            groups: Group = Group.query.join(Group.user_groups).filter(
                User.id == _user.id).filter(Group.name.ilike(f"%{exp.name}%")).all()

            _user.groups = groups

        return flask.jsonify(UserGroupsSchema().dump(_user))


@api_user.route('/<int:user_id>/user/follow')
class SubscribeUser(Resource):
    @api_user.doc(security="apiKey")
    def get(self, user_id):
        """
        Получить подписки и подписчиков конкретного пользователя.
        :param user_id: Какой-то id пользователя
        """
        user_follower: User = User.query.filter_by(id=user_id).first_or_404(description="Пользователь не найден")
        return flask.jsonify(UserActivitySchema().dump(user_follower))
