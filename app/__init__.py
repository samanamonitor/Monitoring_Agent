from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_hashing import Hashing

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
hashing = Hashing(app)

# Add Pull defaults from a MongoDB collection
app.config['PULL_DEFAULTS'] = mongo.db.defaultConfig.find_one(projection={'_id': False})

from app import routes