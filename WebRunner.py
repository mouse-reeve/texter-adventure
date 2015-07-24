''' Runs a dashboard app for texter adventures '''
from flask import Flask, make_response, request
from flask.ext.sqlalchemy import SQLAlchemy
import json
import logging
from sqlalchemy.orm.exc import NoResultFound

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
    try:
        player = db.session.query(models.Player).filter(models.Player.phone == phone_number).one()
    except NoResultFound:
        player = models.Player(name, int(phone_number))
        db.session.add(player)
        db.session.commit()

    turn = GAME.start()
    player.current_turn = turn
    db.session.commit()
    return json.dumps(turn)


@app.route('/api/send/<phone_number>', methods=['POST'])
def send_turn(phone_number):
    ''' manually send a turn, if necessary '''
    turn_data = request.get_json()
    try:
        player = db.session.query(models.Player).filter(models.Player.phone == phone_number).one()
    except NoResultFound:
        return False

    queue = []
    # send a turn
    for text in turn_data['text']:
        logging.info('sending message: %s', text)
        queue.append(TWILIO.send(text, '+%s' % player.phone))

    if len(turn_data['options']):
        options_text = GAME.format_options(turn_data)
        logging.info('sending message: %s', options_text)
        queue.append(TWILIO.send(options_text, '+%s' % player.phone))

    player.turn_history = player.turn_history.append(turn_data) \
                          if player.turn_history else [turn_data]
    db.session.commit()

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

