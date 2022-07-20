from flask_restx import Api, fields

authorizations = {"apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}}

api = Api(version='1.0', title='API VK',
          description='Имитация API VK', doc='/docs/',
          authorizations=authorizations
          )

group = api.model('GroupSchema', {
        'id': fields.Integer,
        'name': fields.String
})

create_group = api.model('CreateGroupSchema', {
        'name': fields.String
})

user = api.model('UserSchema', {
        'username': fields.String,
        'password': fields.String
})
user_group = api.model('UserGroupsSchema', {
        'username': fields.String,
        'groups': fields.Nested(group, as_list=True)
})

user_subscribe = api.model('UserFollowerSchema', {
        'id': fields.Integer,
        'username': fields.String
})