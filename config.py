import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MONGO_URI = os.environ.get('MONGO_URI') or "mongodb://localhost:27017/monitoringAgentDB"
    HASH_SALT = os.environ.get('HASH_SALT')
    PAGINATION_SIZE = int(os.environ.get('PAGINATION_SIZE')) or 50
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    OAUTH_CREDENTIALS={
        'google': {
            'id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET
        }
    }