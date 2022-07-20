import datetime
import flask
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_restx import Resource, Namespace
from vk_api.api.models.user import User
from vk_api.api.models.base import db
from vk_api.api.serializes.user import UserSchema
from vk_api.app.swagger import user

api_auth = Namespace('/', description='Регистрация и получение токена')


@api_auth.route('/register')
class SignupUser(Resource):
    @api_auth.expect(user)
    def post(self):
        """
        Регистрация пользователя.
        """
        data = flask.request.get_json()
        in_user = UserSchema().load(data)
        hashed_password = generate_password_hash(in_user.password, method='sha256')

        _user = User(username=in_user.username, password=hashed_password)

        db.session.add(_user)
        db.session.commit()
        return flask.jsonify({'message': 'registered successfully'})


@api_auth.route('/login')
class LoginUser(Resource):
    @api_auth.expect(user)
    def post(self):
        """
        Аутентификация пользователя.
        """
        auth = flask.request.get_json()
        in_user = UserSchema().load(auth)
        _user = User.query.filter_by(username=in_user.username).first()
        if not in_user or not in_user.username or not in_user.password or not _user:
            return flask.make_response('could not verify', 401, {'Authentication': 'login required"'})

        if check_password_hash(_user.password, in_user.password):
            data = {'identity': _user.id,
                    'exp': datetime.datetime.utcnow() + flask.current_app.config['JWT_EXPIRATION_DELTA']
                    }
            token = jwt.encode(data, flask.current_app.config['SECRET_KEY'], "HS256")
            return flask.jsonify({'token': token.decode("utf-8")})
        return flask.make_response('could not verify', 401, {'Authentication': '"login required"'})
