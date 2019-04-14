from app import app
from app import mongo

@app.route('/', methods = ['POST'])
def index():
    return "Testing!"