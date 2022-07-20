from functools import wraps
import flask
import jwt
from werkzeug.local import LocalProxy
from vk_api.api.models.user import User


current_user = LocalProxy(lambda: getattr(flask._request_ctx_stack.top, 'current_user', None))


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'X-API-Key' in flask.request.headers:
            token = flask.request.headers['X-API-Key']

        if not token:
            return flask.jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, flask.current_app.config['SECRET_KEY'], algorithms=["HS256"])
            flask._request_ctx_stack.top.current_user = User.query.filter_by(id=data['identity']).first()
        except:
            return flask.jsonify({'message': 'token is invalid'})

        return f(*args, **kwargs)

    return decorator
