''' Runs a dashboard app for texter adventures '''
from flask import Flask, make_response, request
from flask.ext.sqlalchemy import SQLAlchemy
import json
import logging

from Gameplay import Gameplay
from IO import TwilioIO

# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/texter_dev'
db = SQLAlchemy(app)

import models

GAME = Gameplay()
TWILIO = TwilioIO()

# ROUTES
@app.route('/')
def index():
    ''' renders the start page '''
    return make_response(open('index.html').read())


@app.route('/api/start/<name>/<phone_number>', methods=['GET'])
def start_game(name, phone_number):
    ''' gets the very beginning of a new game '''
    # lookup or create new player
    phone_number = int(phone_number)
    player = models.Player(name, phone_number)
    db.session.add(player)
    db.session.commit()
    turn = GAME.start()
    return json.dumps(turn)


@app.route('/api/send', methods=['POST'])
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


@app.route('/api/respond', methods=['POST'])
def respond(response):
    ''' the user picks an automated choice with a turn UID '''
    turn_data = request.get_json()
    turn = GAME.process_response(turn_data, response)
    return json.dumps(turn)


if __name__ == '__main__':
    app.debug = True
    app.run(port=4000)

