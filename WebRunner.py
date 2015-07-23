''' Runs a dashboard app for texter adventures '''
from flask import Flask, make_response, request
import json
import logging

from Gameplay import Gameplay
from IO import TwilioIO

# CONFIG
DEBUG = True
APP = Flask(__name__)

GAME = Gameplay()
TWILIO = TwilioIO()

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

    queue = []
    # send a turn
    for text in turn_data['text']:
        logging.info('sending message: %s', text)
        queue.append(TWILIO.send(text, '+15005550006'))

    if len(turn_data['options']):
        options_text = GAME.format_options(turn_data)
        logging.info('sending message: %s', options_text)
        queue.append(TWILIO.send(options_text, '+15005550006'))

    return json.dumps(queue)


@APP.route('/api/respond', methods=['POST'])
def respond(response):
    ''' the user picks an automated choice with a turn UID '''
    turn_data = request.get_json()
    turn = GAME.process_response(turn_data, response)
    return json.dumps(turn)


if __name__ == '__main__':
    APP.debug = True
    APP.run(port=4000)

