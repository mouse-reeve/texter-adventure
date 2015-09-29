''' hello, name, let's play a game '''
from py2neo import Graph
import re

class Gameplay(object):
    ''' defines the course of the game '''

    def __init__(self):
        self.graph = Graph()
        self.autonomous = False
        self.blank_turn = {
            'text': [''],
            'prompt': 'Please select an option:',
            'options': [
                {'pointsTo': None},
                {'pointsTo': None},
                {'pointsTo': None},
                {'text': 'Other', 'pointTo': None}
            ],
            'uid': None
        }


    def start(self, name='dear'):
        ''' selects the entry turn for a new game '''
        return self.get_turn(0, name)


    def get_turn(self, uid, name='dear'):
        ''' load the content of a known turn from the database '''
        turn_data = {'text': [], 'prompt': '', 'options': [], 'uid': uid}

        # get all turn text nodes
        while True:
            current = self.graph.cypher.execute('MATCH (t:turn) WHERE t.uid = %s RETURN t' % uid)
            text = self.format_name(current[0][0]['text'], name)
            turn_data['text'].append(text)
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
                'pointsTo': option[0]['pointsTo'][0] if 'pointsTo' in option[0] else None
            }
            optionset.insert(0, option_dict)

        if uid != 1:
            # "other" options show up after the first turn
            optionset.append({'text': 'Other', 'pointsTo': None})

        turn_data['prompt'] = prompt['text']
        turn_data['options'] = optionset

        return turn_data


    def format_name(self, text, name):
        ''' replaces {FORMATTED} variables with their constant '''
        text = re.sub('{NAME}', name, text)
        return text


    def process_response(self, turn_data, selection, name='dear'):
        ''' determine the selected option '''
        response = clean_response(selection)
        if response['valid']:
            if response['response_id'] < len(turn_data['options']):
                option = turn_data['options'][response['response_id']]
                if 'pointsTo' in option and option['pointsTo']:
                    return self.get_turn(option['pointsTo'], name)
                else:
                    return self.blank_turn

        turn_data['text'] = ['I didn\'t catch that. Can you give me the letter of ' \
                             'the option you wanted?']
        return turn_data


    def format_options(self, turn_data, name='dear'):
        ''' creates the options menu formatted string '''
        prompt = turn_data['prompt']
        options = turn_data['options']
        message = [prompt]
        for (i, option) in enumerate(options):
            text = self.format_name(option['text'], name)
            message.append('%s) %s ' % (chr(ord('A')+i), text))
        return '\n'.join(message)


def clean_response(text):
    ''' basic cleanup to guess what a player may have meant '''
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
    GAME = Gameplay()
    GAME.start()
