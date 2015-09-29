''' Runs a dashboard web app for texter adventures '''
from flask import Flask, make_response, request
import json
import logging
from sqlalchemy.orm.exc import NoResultFound
import time

from Gameplay import Gameplay
from IO import TwilioIO

# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/texter_dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

import models

models.db.init_app(app)

GAME = Gameplay()
TWILIO = TwilioIO()
DELAY = 1


# TEMPLATE

@app.route('/')
def index():
    ''' renders the start page '''
    return make_response(open('index.html').read())


# UTIL

def failure(error):
    ''' formats a failure response '''
    return json.dumps({'success': False, 'data': {'error': error}})


def success(data):
    ''' formats a success response '''
    return json.dumps({'success': True, 'data': data})


# API

@app.route('/api/player', methods=['POST'])
def add_player():
    ''' create a new entry in the player table '''
    data = request.get_json()
    try:
        player = models.add_player(data['name'], data['phone'])
    except KeyError:
        return failure('name or phone number not found')

    turn = GAME.start(player.name)
    player.set_pending_turn(turn)
    return success({})

@app.route('/api/player/new', methods=['GET'])
def start_game():
    ''' load a game '''
    player = models.get_uncontacted_player()
    player.set_show(True)
    return success({})


@app.route('/api/message/<phone>', methods=['POST'])
def send_turn(phone):
    ''' manually send a turn '''
    turn_data = request.get_json()
    try:
        player = models.find_player(phone)
    except NoResultFound:
        return failure('no player found with that phone number')

    player = player.set_contacted(True)

    # send a turn
    queue = []
    for text in turn_data['text']:
        logging.info('sending message: %s', text)
        sms = TWILIO.send(text, '+%s' % player.phone)
        queue.append(sms)
        time.sleep(DELAY)

        models.add_message(player, turn_data, sms)

    if 'options' in turn_data and len(turn_data['options']):
        options_text = GAME.format_options(turn_data, player.name)
        logging.info('sending message: %s', options_text)
        sms = TWILIO.send(options_text, '+%s' % player.phone)
        queue.append(sms)
        time.sleep(DELAY)

        models.add_message(player, turn_data, sms)

    return success(queue)


@app.route('/api/respond', methods=['POST'])
def respond():
    ''' receives a reply from twilio '''
    sms = request.values.to_dict()
    phone = sms['From'].replace('+', '')

    try:
        player = models.find_player(phone)
    except NoResultFound:
        # contact from an unknown number
        player = models.add_player(None, phone)

        turn_data = {'text': ['Pardon me, but what name do you go by?'], 'uid': None}
        player.set_pending_turn(turn_data)
        return success(player.pending_turn)
    else:
        player.set_show(True)

        # TODO: this is maybe the wrong way to get this
        previous_turn = player.pending_turn

        turn = GAME.process_response(previous_turn, sms['Body'], player.name)
        player.set_pending_turn(turn)

        models.add_message(player, {'text': sms['Body']}, sms, incoming=True)

        return success(turn)


@app.route('/api/player', methods=['GET'])
def get_games():
    ''' gets all game data '''
    players = models.get_visible_players()
    data = []
    for player in players:
        data.append(player.serialize())
    return success(data)


@app.route('/api/player/<phone>', methods=['GET'])
def get_history(phone):
    ''' gets the history of a single game '''
    player = models.find_player(phone)
    return success(player.serialize())


@app.route('/api/player/<phone>', methods=['PUT'])
def update_player(phone):
    ''' show or hide a game '''
    data = request.get_json()
    player = models.find_player(phone)

    if 'name' in data:
        player.name = data['name']
    if 'show' in data:
        player.show = data['show']
    if 'notes' in data:
        player.notes = data['notes']
    player.save()
    return success(player.serialize())


@app.route('/api/player/<phone>/<uid>', methods=['PUT'])
def set_current_turn(uid, phone):
    ''' shift the current pending turn to a given uid '''
    player = models.find_player(phone)
    turn = GAME.get_turn(uid, player.name)
    player.set_pending_turn(turn)
    return json.dumps(turn)


if __name__ == '__main__':
    app.debug = True
    app.run(port=4000)
