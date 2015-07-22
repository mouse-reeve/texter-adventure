''' Runs a dashboard app for texter adventures '''
from flask import Flask, make_response, request
import json

from Gameplay import Gameplay

# CONFIG
DEBUG = True
APP = Flask(__name__)

GAME = Gameplay()

# ROUTES
@APP.route('/')
def index():
    ''' renders the start page '''
    return make_response(open('index.html').read())


@APP.route('/api/start', methods=['GET'])
def start_game():
    ''' gets the very beginning of a new game '''
    turn = GAME.start()
    return json.dumps(turn)


@APP.route('/api/send', methods=['POST'])
def send_turn():
    ''' manually send a turn, if necessary '''
    turn_data = request.get_json()
    turn = GAME.send_turn(turn_data)
    return json.dumps(turn)


@APP.route('/api/respond/<response>', methods=['POST'])
def respond(response):
    ''' the user picks an automated choice with a turn UID '''
    turn_data = request.get_json()
    turn = GAME.process_response(turn_data, response)
    return json.dumps(turn)


if __name__ == '__main__':
    APP.debug = True
    APP.run(port=4000)

