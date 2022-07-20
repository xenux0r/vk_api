import datetime

SECRET_KEY = 'b98432ebf0522a414b8b0bf3f1195362'
JWT_AUTH_HEADER_PREFIX = 'Bearer'
SQLALCHEMY_DATABASE_URI = 'postgresql://docker:docker@localhost/api_vk'
JWT_EXPIRATION_DELTA = datetime.timedelta(minutes=60)
