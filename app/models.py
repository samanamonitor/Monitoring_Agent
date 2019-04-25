from flask_login import UserMixin
from app import login, mongo
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, data):
        self.id = data['_id']
        self.email = data['email']

@login.user_loader
def load_user(id):
    return User(mongo.db.users.find_one(ObjectId(id)))