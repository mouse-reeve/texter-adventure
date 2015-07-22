''' Runs a dashboard app for texter adventures '''
from flask import Flask, make_response
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
    return json.dumps(turn['text'])

@APP.route('/api/send', methods=['GET'])
def send_turn():
    ''' manually send a turn, if necessary '''
    turn = GAME.confirm_turn()
    return json.dumps(turn['text'])

@APP.route('/api/choice/<turn_uid>')
def automatic_choice(turn_id):
    ''' the user picks an automated choice with a turn UID '''
    success = GAME.automatic_turn(turn_id)
    return json.dumps({'success': success})

if __name__ == '__main__':
    APP.debug = True
    APP.run(port=4000)

