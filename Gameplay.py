''' hello, name, let's play a game '''
import logging
from py2neo import Graph
import re
from concurrent.futures import ThreadPoolExecutor

from IO import SysIO, TwilioIO

class Gameplay(object):
    ''' defines the course of the game '''

    def __init__(self, comms=TwilioIO):
        self.graph = Graph()
        self.params = {'NAME': 'Alice'}
        self.comms = comms()
        self.current_turn = {}
        self.autonomous = False


    def start(self):
        ''' initialize and accesses the first turn in a game '''
        return self.automatic_turn(0)


    def automatic_turn(self, uid):
        ''' gets a turn within the known graph '''

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
            option = option[0]
            optionset.insert(0, option)

        turn_data['prompt'] = prompt['text']
        turn_data['options'] = optionset

        return self.turn(turn_data)


    def custom_turn(self, turn_data):
        ''' runs a custom, on-the-fly generated turn '''
        #return self.turn(turn_data)


    def error_turn(self, turn_data):
        ''' game handles input it doesn't understand '''
        turn_data['text'] = ['I didn\'t catch that. Can you give me the letter of ' \
                             'the option you wanted?']
        #return self.turn(turn_data)

    def turn(self, turn_data):
        ''' runs a turn '''
        self.current_turn = turn_data
        if self.autonomous:
            self.confirm_turn()

        return self.current_turn


    def confirm_turn(self):
        ''' allows the system to wait on GM confirmation '''
        # send a turn
        for text in self.current_turn['text']:
            logging.info('sending message: %s', text)
            self.send_message(text)

        if len(self.current_turn['options']):
            options_text = format_options(self.current_turn['prompt'], self.current_turn['options'])
            logging.info('sending message: %s', options_text)
            self.send_message(options_text)

            # get the response
            self.pick_option()


    def send_message(self, message):
        ''' pass the turn info to the player '''
        message = self.format_vars(message)
        success = self.comms.send(message)
        if not success:
            logging.error('Failed to send message')


    def format_vars(self, text):
        ''' replaces {FORMATTED} variables with their constant '''
        for key, value in self.params.items():
            text = re.sub('{%s}' % key, value, text)
        return text


    def pick_option(self):
        ''' determine the selected option '''
        executor = ThreadPoolExecutor(max_workers=2)
        return executor.submit(self.comms.receive).add_done_callback(self.response_ready)


    def response_ready(self, future):
        ''' handles the user input '''
        response = future.result()

        options = self.current_turn['options']
        if response['valid'] and response['response_id'] < len(options):
            selection = options[response['response_id']]
            if not 'pointsTo' in selection:
                return self.custom_turn(self.comms.get_custom(self.current_turn))
            return self.automatic_turn(selection['pointsTo'][0])
        return self.error_turn(self.current_turn)


    def custom_response(self):
        ''' GM intercedes to determine response to player '''
        logging.warn('Custom handling required')
        return self.comms.get_custom()


def format_options(prompt, options):
    ''' creates the options menu formatted string '''
    message = [prompt]
    for (i, option) in enumerate(options):
        message.append('%s) %s ' % (chr(ord('A')+i), option['text']))
    return '\n'.join(message)


if __name__ == '__main__':
    GAME = Gameplay(SysIO)
    GAME.start()
