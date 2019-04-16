import os

class Config(object):
    MONGO_URI = os.environ.get('MONGO_URI') or "mongodb://localhost:27017/monitoringAgentDB"
    HASH_SALT = os.environ.get('HASH_SALT')