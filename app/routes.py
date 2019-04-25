from flask import request, Response, jsonify, render_template
from app import app, mongo, hashing
from bson.objectid import ObjectId
import time, json

@app.route('/')
def index():
    servers = mongo.db.agentData.find(projection={'key': False})
    return render_template('index.html', title='Home', servers=servers, time=time)

@app.route('/agent/config')
def config():
    # This is the default pull config
    d = app.config['PULL_DEFAULTS'].copy()

    # Ensure that all values are accounted from url args
    # to create key to find config
    if request.args.get('guid') is None or \
        request.args.get('hostname') is None or \
            request.args.get('domain') is None:
        return render_template('errors/404.html'), 400

    key = request.args['guid'] + ',' + request.args['hostname'] + ',' + request.args['domain']
    key = hashing.hash_value(key, salt= app.config['HASH_SALT'])

    # Contains the config changes for this particular client
    config = mongo.db.clientConfigs.find_one({'key': key}, projection={'_id': False, 'key': False})

    # Modify the the configuration accordingly
    if config is not None:
        for k,v in config.items():
            d[k] = v

    return render_template(
        'config.html', 
        guid=request.args['guid'], 
        hostname=request.args['hostname'], 
        domain=request.args['domain'], 
        config=d
    )

@app.route('/agent/data/<dataID>')
def data(dataID):

    datum = mongo.db.agentData.find_one_or_404({'_id': ObjectId(dataID)})
    serial = datum['data']

    res = Response(serial)
    res.headers['Content-Type'] = 'application/json'

    return res

@app.route('/PULL')
def pull():

    # This is the default pull config
    d = app.config['PULL_DEFAULTS'].copy()

    # Ensure that all values are accounted from url args
    # to create key to find config
    if request.args.get('guid') is None or \
        request.args.get('hostname') is None or \
            request.args.get('domain') is None:
        return 'Bad request', 400

    key = request.args['guid'] + ',' + request.args['hostname'] + ',' + request.args['domain']
    key = hashing.hash_value(key, salt= app.config['HASH_SALT'])

    # Contains the config changes for this particular client
    config = mongo.db.clientConfigs.find_one({'key': key}, projection={'_id': False, 'key': False})

    # Modify the the configuration accordingly
    if config is not None:
        for k,v in config.items():
            d[k] = v

    return jsonify(d), 200

@app.route('/PUSH', methods = ['POST'])
def push():
    if not request.is_json:
        return 'Bad request. Not JSON.', 400

    # Ensure that that the POST body has the minimum required values
    d = request.get_json()
    if d['post'].get('guid') is None or \
        d['post'].get('hostname') is None or \
            d['post'].get('domain') is None:
        return 'Bad request', 400
    
    guid = d['post'].get('guid')
    hostname = d['post'].get('hostname')
    domain = d['post'].get('domain')
    uploadTime = d['post'].get('UploadTime')

    key = guid + ',' + hostname + ',' + domain
    key = hashing.hash_value(key, salt= app.config['HASH_SALT'])

    dataToSet = {
        'guid':guid, 
        'hostname':hostname, 
        'domain':domain, 
        'uploadTime':uploadTime, 
        'data':request.get_data(),
    }

    # Record the incoming data serialized
    mongo.db.agentData.update_one(
        filter={'key': key}, 
        update={'$set': dataToSet}, 
        upsert=True
    )

    return 'Okay', 200

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404