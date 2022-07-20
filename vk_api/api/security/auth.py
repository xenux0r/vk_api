import datetime
import flask
import jwt
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Resource, Namespace
from vk_api.api.models.user import User
from vk_api.api.models.base import db
from vk_api.api.serializes.user import CreateUserSchema
from vk_api.app.swagger import create_user
from vk_api.app.error.error import make_error

api_auth = Namespace('/', description='Регистрация и получение токена')


@api_auth.route('/register')
class SignupUser(Resource):
    @api_auth.expect(create_user)
    def post(self):
        """
        Регистрация пользователя.
        """
        data = flask.request.get_json()
        in_user = CreateUserSchema().load(data)
        hashed_password = generate_password_hash(in_user.password, method='sha256')

        _user = User(username=in_user.username, password=hashed_password)
        try:
            db.session.add(_user)
            db.session.commit()
        except IntegrityError as e:
            if e.orig.pgcode in ['23505']:
                return make_error(status_code=406, message="Это имя уже занято")

        return flask.jsonify({'message': 'registered successfully'})


@api_auth.route('/auth')
class LoginUser(Resource):
    @api_auth.expect(create_user)
    def post(self):
        """
        Аутентификация пользователя.
        """
        auth = flask.request.get_json()
        in_user = CreateUserSchema().load(auth)
        _user = User.query.filter_by(username=in_user.username).first()
        if not in_user or not in_user.username or not in_user.password or not _user:
            return flask.make_response('could not verify', 401, {'Authentication': 'login required"'})

        if check_password_hash(_user.password, in_user.password):
            data = {'identity': _user.id,
                    'exp': datetime.datetime.utcnow() + flask.current_app.config['JWT_EXPIRATION_DELTA']
                    }
            token: str = jwt.encode(data, flask.current_app.config['SECRET_KEY'], "HS256")
            return flask.jsonify({'token': token})
        return flask.make_response('could not verify', 401, {'Authentication': '"login required"'})
