from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_hashing import Hashing
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)
hashing = Hashing(app)
login = LoginManager(app)
login.login_view = 'login'
login.session_protection = 'strong'
bootstrap = Bootstrap(app)

# Add Pull defaults from a MongoDB collection
app.config['PULL_DEFAULTS'] = mongo.db.defaultConfig.find_one(projection={'_id': False})

# Add elasticsearch to the app
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

from app import routes