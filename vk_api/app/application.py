import flask
from vk_api.api.handlers.user import api_user
from vk_api.api.handlers.group import api_group
from vk_api.api.models.base import db, migrate
from vk_api.api.security.auth import api_auth
from vk_api.app.swagger import api


def create_app():
    app = flask.Flask(__name__)

    app.config.from_pyfile('config..py')
    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)
    api.add_namespace(api_user)
    api.add_namespace(api_group)
    api.add_namespace(api_auth)

    @app.cli.command()
    def createdb():
        db.create_all()


    return app

