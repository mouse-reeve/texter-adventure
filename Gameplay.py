''' hello, name, let's play a game '''
from ConfigParser import SafeConfigParser
import logging
from py2neo import Graph
import random
import re
import sys

from IO import SysIO

def start():
    ''' initualize and accesses the first turn in a game '''
    turn('START')


def turn(uid):
    ''' runs a turn '''

    turns = GRAPH.cypher.execute('MATCH (t:turn) WHERE t.uid = "%s" RETURN t' % uid)
    options = GRAPH.cypher.execute('MATCH (t:turn) --> (o:option) '
                                   'WHERE t.uid = "%s" '
                                   'RETURN o' % uid)
    turn_node = turns[0][0]

    for text in turn_node['text']:
        send_message(text)

    optionset = []
    for option in options:
        option = option[0]
        optionset.insert(0, option)

    if len(options):
        send_message(format_options(optionset))

        selection = pick_option(optionset)
        turn(selection['destination'])


def send_message(message):
    ''' pass the turn info to the player '''
    message = format_vars(message)
    success = IO.send(message)
    if not success:
        LOGGER.error('Failed to send message')


def format_options(options):
    ''' creates the options menu formatted string '''
    message = ['Please select an option: ']
    for (i, option) in enumerate(options):
        message.append('%s) %s ' % (chr(ord('A')+i), option['text']))
    return '\n'.join(message)


def format_vars(text):
    ''' replaces {FORMATTED} variables with their constant '''
    for key, value in VARS.items():
        text = re.sub('{%s}' % key, value, text)
    return text


def pick_option(options):
    ''' determine the selected option '''
    response = IO.receive()
    if response['valid'] and response['response_id'] < len(options):
        return options[response['response_id']]
    else:
        LOGGER.warn('invalid response, picking at random')

    return random.choice(options)


if __name__ == '__main__':
    GRAPH = Graph()

    HANDLER = logging.StreamHandler()
    HANDLER.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    LOGGER = logging.getLogger()
    LOGGER.addHandler(HANDLER)
    LOGGER.setLevel(logging.WARN)

    VARS = {}
    try:
        VARS['NAME'] = sys.argv[1]
    except IndexError:
        LOGGER.error('Please provide the player name')
    else:
        PARSER = SafeConfigParser()
        PARSER.read('settings.ini')
        if PARSER.get('environment', 'debug'):
            IO = SysIO()
        else:
            LOGGER.warn('no prod IO available')
            IO = SysIO()

        start()
