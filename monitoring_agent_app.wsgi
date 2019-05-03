import os, sys
from dotenv import load_dotenv

# Use virtual environment in project path 
activate_this = os.path.dirname(os.path.realpath(__file__)) + '/venv/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Add project to path variable
path = '/var/www/Monitoring_Agent'
if path not in sys.path:
    sys.path.append(path)

# Load environmental variables
load_dotenv('/var/www/Monitoring_Agent/.flaskenv')

# Assign flask app as WSGI application
from app import app as application