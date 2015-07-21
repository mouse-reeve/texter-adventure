''' Runs a dashboard app for texter adventures '''
from flask import Flask, make_response

# CONFIG
DEBUG = True
APP = Flask(__name__)

# ROUTES
@APP.route('/')
def index():
    ''' renders the start page '''
    return make_response(open('index.html').read())

if __name__ == '__main__':
    APP.debug = True
    APP.run(port=4000)

