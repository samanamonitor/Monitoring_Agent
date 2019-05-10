from flask import request, Response, jsonify, render_template, redirect, url_for, send_file, g
from flask_login import current_user, login_user, logout_user, login_required
from app import app, mongo, hashing
from app.auth import OAuthSignIn
from app.models import User
from app.forms import EditConfigField, SearchForm
from app.search import add_to_index, query_index
from bson.objectid import ObjectId
import time, json
from app.helpers import changes

@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()

@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    if page < 1:
        return redirect(url_for('index'))
    
    prev_page = page - 1
    if prev_page < 1:
        prev_page = None
    next_page = None
    count = mongo.db.agentData\
        .find(projection={'_id': False})\
        .skip((page)*app.config['PAGINATION_SIZE'])\
        .count(True)

    if count > 0:
        next_page = page + 1

    servers = mongo.db.agentData\
        .find()\
        .skip((page-1)*app.config['PAGINATION_SIZE'])\
        .limit(app.config['PAGINATION_SIZE'])
    return render_template(
        'index.html', 
        title='Home', 
        servers=servers, 
        time=time, 
        prev_page=prev_page, 
        next_page=next_page
    )

@app.route('/search')
def search():
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    keys, total = query_index(
        index='agentdata', 
        query=g.search_form.q.data, 
        page=page, 
        per_page=app.config['PAGINATION_SIZE']
    )
    servers = mongo.db.agentData.find({'key': {'$in': keys}})
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if total > page * app.config['PAGINATION_SIZE'] else None

    return render_template(
        'search.html', 
        title='Search',
        servers=servers,
        time=time,
        prev_page=prev_page, 
        next_page=next_page
    )

@app.route('/get-agent-side-tool')
def getAgentSideTool():
    try:
        return send_file('static/agent_side_script.zip', attachment_filename='agent_side_script.zip')
    except Exception as e:
        return str(e)

@app.route('/agent/config')
@login_required
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
    isDefault = True
    if config is not None:
        isDefault = False
        for k,v in config.items():
            d[k] = v

    return render_template(
        'config.html', 
        guid=request.args['guid'], 
        hostname=request.args['hostname'], 
        domain=request.args['domain'], 
        config=d,
        isDefault=isDefault
    )

@app.route('/agent/config/edit', methods=['GET', 'POST'])
@login_required
def editConfig():
    # Ensure that all values are accounted from url args
    # to edit the corresponding config
    if request.args.get('guid') is None or \
        request.args.get('hostname') is None or \
            request.args.get('domain') is None:
        return render_template('errors/404.html'), 400

    key = request.args['guid'] + ',' + request.args['hostname'] + ',' + request.args['domain']
    key = hashing.hash_value(key, salt= app.config['HASH_SALT'])

    form=EditConfigField(key)
    d = app.config['PULL_DEFAULTS']
    if form.validate_on_submit():
        configChanges = changes(d, form.toDict())
        if len(configChanges) > 0:
            mongo.db.clientConfigs.update_one(
                {'key': key},
                update={'$set': configChanges}, 
                upsert=True
            )
        else:
            mongo.db.clientConfigs.delete_one({'key': key})
        return redirect(
            url_for('config') + '?guid=' + request.args['guid'] + '&hostname=' + request.args['hostname'] + '&domain=' + request.args['domain']
        )
    elif request.method == 'GET':
        data = mongo.db.clientConfigs.find_one({'key': key}, projection={'_id': False, 'key': False})
        if data is not None:
            for k,v in data.items():
                d[k] = v
        form.config_interval.data = d.get('config_interval')
        form.FileVersionMS.data = d.get('FileVersionMS')
        form.logs.data = ','.join(d.get('logs'))
        form.cpu_interval.data = d.get('cpu_interval')
        form.FileVersionLS.data = d.get('FileVersionLS')
        form.data_url.data = d.get('data_url')
        form.num.data = d.get('num')
        form.MonitorPath.data = d.get('MonitorPath')
        form.debug.data = d.get('debug')
        form.upload_interval.data = d.get('upload_interval')

    return render_template(
        'edit_config.html', 
        form=form, 
        hostname=request.args['hostname'], 
        domain=request.args['domain']
    )

# Reset config changes to deafault values
@app.route('/agent/config/reset')
def resetConfig():
    # Ensure that all values are accounted from url args
    # to edit the corresponding config
    if request.args.get('guid') is None or \
        request.args.get('hostname') is None or \
            request.args.get('domain') is None:
        return render_template('errors/404.html'), 400

    key = request.args['guid'] + ',' + request.args['hostname'] + ',' + request.args['domain']
    key = hashing.hash_value(key, salt= app.config['HASH_SALT'])

    mongo.db.clientConfigs.delete_one({'key': key})

    return redirect(
        url_for('config') + '?guid=' + request.args['guid'] + '&hostname=' + request.args['hostname'] + '&domain=' + request.args['domain']
    )

# Ajax endpoint for index page
@app.route('/agent/data/<key>')
def data(key):

    datum = mongo.db.agentData.find_one_or_404({'key': key})
    serial = datum['data']

    res = Response(serial)
    res.headers['Content-Type'] = 'application/json'

    return res

@app.route('/PULL')
def pull():

    # This is the default pull config
    d = app.config['PULL_DEFAULTS'].copy()

    # Ensure that all values are accounted from url args
    # to create key to find config or else send default config
    if request.args.get('guid') is None or \
        request.args.get('hostname') is None or \
            request.args.get('domain') is None:
        return jsonify(d), 200

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
    result = mongo.db.agentData.update_one(
        filter={'key': key}, 
        update={'$set': dataToSet}, 
        upsert=True
    )

    if result.upserted_id is not None:
        print("I'm in!")
        add_to_index(index='agentdata', key=key, doc={'hostname':hostname, 'domain':domain})

    return 'Okay', 200

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/oauth/google')
def google_authorize():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider('google')
    return oauth.authorize()



@app.route('/oauth/google/callback')
def google_callback():
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    
    oauth = OAuthSignIn.get_provider('google')
    email = oauth.callback()

    if email is None:
        return redirect(url_for('login'))

    user = mongo.db.users.find_one({'email': email})
    if user is None:
        id = mongo.db.users.insert({'email': email})
        user = mongo.db.users.find_one({'_id': id})
    
    login_user(User(user), remember=False)
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

