import sys
from dotenv import load_dotenv

# Add project to path variable
path = '/var/www/Monitoring_Agent'
if path not in sys.path:
    sys.path.append(path)

# Load environmental variables
load_dotenv('/var/www/Monitoring_Agent/.flaskenv')

# Assign flask app as WSGI application
from app import app as application