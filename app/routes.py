from flask import request, jsonify
from app import app, mongo, hashing

@app.route('/PULL', methods = ['GET'])
def pull():
    d = {
        "config_interval": 30000,
        "domain": "",
        "FileVersionMS": 65536,
        "logs": [
            "System",
            "Application"
        ],
        "cpu_interval": 1000,
        "hostname": "WIN-67T1P3TI72F",
        "FileVersionLS": 1,
        "data_url": "https://admin.samana.cloud/monitor/data",
        "num": 100,
        "MonitorPath": "https://s3-us-west-2.amazonaws.com/monitor.samanagroup.co/Monitor.exe",
        "debug": 0,
        "upload_interval": 10000,
        "guid": "f8cf06e3-36e6-47ce-b766-bb3387821afb"
    }
    return jsonify(d), 200

@app.route('/PUSH', methods = ['POST'])
def push():
    if not request.is_json:
        return 'Bad Request. Not JSON.', 400

    d = request.get_json()
    key = ''

    try:
        key = d['post']['guid'] + ',' + d['post']['hostname'] + ',' + d['post']['domain']
        key = hashing.hash_value(key, salt= app.config['HASH_SALT'])
    except:
        return 'Bad Request', 400

    mongo.db.agentData.insert_one({'key': key, 'data': request.get_data()})

    return 'Okay', 200