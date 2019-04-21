from flask import request, jsonify
from app import app, mongo, hashing

@app.route('/PULL', methods = ['GET'])
def pull():

    # This is the default pull config
    d = app.config['PULL_DEFAULTS']

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

    key = d['post']['guid'] + ',' + d['post']['hostname'] + ',' + d['post']['domain']
    key = hashing.hash_value(key, salt= app.config['HASH_SALT'])

    # Record the incoming data serialized
    mongo.db.agentData.update_one(
        filter={'key': key}, 
        update={'$set':{'data': request.get_data()}}, 
        upsert=True
    )

    return 'Okay', 200