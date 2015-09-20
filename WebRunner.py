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
        player = find_player(phone_number)
    except NoResultFound:
        player = models.Player(name, int(phone_number))
        db.session.add(player)
        db.session.commit()

    turn = GAME.start()
    player.current_turn = turn;
    db.session.commit()
    return json.dumps(turn)


@app.route('/api/send/<phone_number>', methods=['POST'])
def send_turn(phone_number):
    ''' manually send a turn, if necessary '''
    turn_data = request.get_json()
    try:
        player = find_player(phone_number)
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

    update_turn_log(player, turn_data)

    return json.dumps(queue)


@app.route('/api/respond', methods=['POST'])
def respond():
    ''' receives a reply from twilio '''
    sms = request.get_json()
    player = find_player(sms['From'])
    turn_data = player.current_turn
    update_turn_log(player, sms, response=True)

    turn = GAME.process_response(turn_data, sms['Body'])
    return json.dumps(turn)


@app.route('/api/games', methods=['GET'])
def games():
    players = db.session.query(models.Player).all()
    games = [{
        'turn_history': p.turn_history,
        'current_turn': p.current_turn,
        'name': p.name,
        'phone': p.phone} for p in players]
    return json.dumps(games)


@app.route('/api/history/<phone_number>', methods=['GET'])
def history(phone_number):
    player = find_player(phone_number)
    return json.dumps(player.turn_history)


def find_player(phone_number):
    return db.session.query(models.Player).filter(models.Player.phone == phone_number).one()


def update_turn_log(player, turn_data, response=False):
    turn_type = 'response'
    if not response:
        turn_type = 'turn'
        player.current_turn = turn_data
    history = player.turn_history[:]
    history.append({'type': turn_type, 'content': turn_data})
    player.turn_history = history
    db.session.commit()

if __name__ == '__main__':
    app.debug = True
    app.run(port=4000)

