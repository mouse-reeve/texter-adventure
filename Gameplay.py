''' hello, name, let's play a game '''
from ConfigParser import SafeConfigParser
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
    IO.send(message)


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
    data = clean_response(response, len(options))
    if data['valid']:
        return options[data['response_id']]
    else:
        print 'invalid response, picking at random'

    return random.choice(options)

def clean_response(text, option_count):
    ''' try to determine what the player wants to do '''
    data = {'valid': False, 'original': text, 'response_id': None}

    text = re.sub(r'\(|\)|\.', '', text)

    # Check for simple numerical response
    try:
        response = int(text) - 1
        data['valid'] = True
        data['response_id'] = response
        return data
    except ValueError:
        pass

    # check for alphabet response
    if len(text) == 1:
        data['valid'] = True
        if ord(text) >= ord('A') and ord(text) <= ord('Z'):
            data['response_id'] = ord(text) - ord('A')
        elif ord(text) >= ord('a') and ord(text) <= ord('z'):
            data['response_id'] = ord(text) - ord('a')
        else:
            data['valid'] = False

    if data['valid'] and (data['response_id'] < 0 or data['response_id'] > option_count):
        data['valid'] = False

    return data


if __name__ == '__main__':
    GRAPH = Graph()

    VARS = {}
    try:
        VARS['NAME'] = sys.argv[1]
    except IndexError:
        print 'Please provide the player name'
    else:
        PARSER = SafeConfigParser()
        PARSER.read('settings.ini')
        if PARSER.get('environment', 'debug'):
            IO = SysIO()
        else:
            print 'no prod IO available'
            IO = SysIO()

        start()
