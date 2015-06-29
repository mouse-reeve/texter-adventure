''' hello, name, let's play a game '''
from py2neo import Graph
import random
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
    IO.send(message)


def format_options(options):
    ''' creates the options menu formatted string '''
    message = ['Please select an option: ']
    for (i, option) in enumerate(options):
        message.append('%d) %s ' % (i+1, option['text']))
    return '\n'.join(message)


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
    NAME = sys.argv[1]
    IO = SysIO()
    start()
