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
        message.append('%d) %s ' % (i+1, option['text']))
    return '\n'.join(message)


def format_vars(text):
    for key, value in VARS.items():
        text = re.sub('{%s}' % key, value, text)
    return text


def pick_option(options):
    ''' determine the selected option '''
    response = IO.receive()
    try:
        response = int(response) - 1
        if response < len(options):
            return options[response]
    except ValueError:
        print 'invalid response, picking at random'

    return random.choice(options)


if __name__ == '__main__':
    GRAPH = Graph()

    VARS = {}
    try:
        VARS['NAME'] = sys.argv[1]
    except IndexError:
        VARS['NAME']  = "John Doe"

    PARSER = SafeConfigParser()
    PARSER.read('settings.ini')
    if PARSER.get('environment', 'debug'):
        IO = SysIO()
    else:
        #TODO: add twilio IO
        IO = SysIO()

    start()
