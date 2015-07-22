''' hello, name, let's play a game '''
import logging
from py2neo import Graph
import re

from IO import SysIO, TwilioIO

class Gameplay(object):
    ''' defines the course of the game '''

    def __init__(self, comms=TwilioIO):
        self.graph = Graph()
        self.params = {'NAME': 'Alice'}
        self.comms = comms()
        self.autonomous = False


    def start(self):
        ''' selects the entry turn for a new game '''
        return self.get_turn(0)


    def get_turn(self, uid):
        ''' load the content of a known turn from the database '''
        turn_data = {'text': [], 'prompt': '', 'options': [], 'uid': uid}

        # get all turn text nodes
        while True:
            current = self.graph.cypher.execute('MATCH (t:turn) WHERE t.uid = %s RETURN t' % uid)
            turn_data['text'].append(current[0][0]['text'])
            try:
                uid = self.graph.cypher.execute('MATCH t --> (t2:turn) ' \
                                           'WHERE t.uid = %s RETURN t2' % uid)[0][0]['uid']
                turn_data['uid'] = uid
            except IndexError:
                break

        prompt = self.graph.cypher.execute('MATCH (t:turn) --> (p:prompt) '
                                           'WHERE t.uid = %s '
                                           'RETURN p' % uid)
        try:
            prompt = prompt[0][0]
            options = self.graph.cypher.execute('MATCH (p:prompt) --> (o:option) '
                                                'WHERE p.uid = %s '
                                                'RETURN o' % prompt['uid'])
        except IndexError:
            prompt = {'text': ''}
            options = []

        optionset = []
        for option in options:
            option_dict = {
                'text': option[0]['text'],
                'pointsTo': option[0]['pointsTo'] if 'pointsTo' in option[0] else None
            }
            optionset.insert(0, option_dict)

        turn_data['prompt'] = prompt['text']
        turn_data['options'] = optionset

        return turn_data


    def send_turn(self, turn_data):
        ''' allows the system to wait on GM confirmation '''
        turn_success = True
        # send a turn
        for text in turn_data['text']:
            logging.info('sending message: %s', text)
            success = self.send_message(text)
            turn_success = success if not success else turn_success

        if len(turn_data['options']):
            options_text = format_options(turn_data['prompt'], turn_data['options'])
            logging.info('sending message: %s', options_text)
            success = self.send_message(options_text)
            turn_success = success if not success else turn_success

        return turn_success


    def send_message(self, message):
        ''' pass the turn info to the player '''
        message = self.format_vars(message)
        success = self.comms.send(message)
        if not success:
            logging.error('Failed to send message')

        return success


    def format_vars(self, text):
        ''' replaces {FORMATTED} variables with their constant '''
        for key, value in self.params.items():
            text = re.sub('{%s}' % key, value, text)
        return text


    def process_response(self, turn_data, selection):
        ''' determine the selected option '''
        response = clean_response(selection)
        if response['valid']:
            if response['response_id'] < len(turn_data['options']):
                option = turn_data['options'][response['response_id']]
                if 'pointsTo' in option:
                    return self.get_turn(option['pointsTo'][0])

        turn_data['text'] = ['I didn\'t catch that. Can you give me the letter of ' \
                             'the option you wanted?']
        return turn_data


def format_options(prompt, options):
    ''' creates the options menu formatted string '''
    message = [prompt]
    for (i, option) in enumerate(options):
        message.append('%s) %s ' % (chr(ord('A')+i), option['text']))
    return '\n'.join(message)


def clean_response(text):
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

    if data['valid'] and (data['response_id'] < 0):
        data['valid'] = False

    return data


if __name__ == '__main__':
    GAME = Gameplay(SysIO)
    GAME.start()
