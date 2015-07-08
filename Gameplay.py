''' hello, name, let's play a game '''
from ConfigParser import SafeConfigParser
import logging
from py2neo import Graph
import re
import sys

from IO import SysIO

def start():
    ''' initualize and accesses the first turn in a game '''
    automatic_turn(0)


def automatic_turn(uid):
    ''' gets a turn within the known graph '''

    text = []

    while True:
        current = GRAPH.cypher.execute('MATCH (t:turn) WHERE t.uid = %s RETURN t' % uid)
        text.append(current[0][0]['text'])
        try:
            uid = GRAPH.cypher.execute('MATCH t --> (t2:turn) ' \
                                       'WHERE t.uid = %s RETURN t2' % uid)[0][0]['uid']
        except:
            break

    prompt = GRAPH.cypher.execute('MATCH (t:turn) --> (p:prompt) '
                                  'WHERE t.uid = %s '
                                  'RETURN p' % uid)
    try:
        prompt = prompt[0][0]
        options = GRAPH.cypher.execute('MATCH (p:prompt) --> (o:option) '
                                       'WHERE p.uid = %s '
                                       'RETURN o' % prompt['uid'])
    except:
        prompt = {'text': ''}
        options = []

    optionset = []
    for option in options:
        option = option[0]
        optionset.insert(0, option)

    turn(text, prompt['text'], optionset)


def custom_turn(turn_data):
    ''' runs a custom, on-the-fly generated turn '''
    turn(turn_data['text'], turn_data['prompt'], turn_data['options'])


def turn(texts, prompt, options):
    ''' runs a turn '''

    for text in texts:
        LOGGER.info('sending message: %s', text)
        send_message(text)

    if len(options):
        options_text = format_options(prompt, options)
        LOGGER.info('sending message: %s', options_text)
        send_message(options_text)

        selection = pick_option(options)
        if selection:
            automatic_turn(selection['pointsTo'][0])
        else:
            selection = custom_response()
            custom_turn(selection)


def send_message(message):
    ''' pass the turn info to the player '''
    message = format_vars(message)
    success = IO.send(message)
    if not success:
        LOGGER.error('Failed to send message')


def format_options(prompt, options):
    ''' creates the options menu formatted string '''
    message = [prompt]
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
        return False


def custom_response():
    ''' GM intercedes to determine response to player '''
    LOGGER.warn('Custom handling required')
    return IO.get_custom()


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
