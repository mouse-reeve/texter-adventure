''' The interface for performing I/O to the player '''
import re
import time

def create_response(text):
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


class AbstractIO(object):
    ''' Defines basic types of communication (in and out) '''

    def send(self, text):
        ''' Prompt the player with a scene or options '''
        raise NotImplementedError()

    def receive(self):
        ''' Get an answer from the player '''
        raise NotImplementedError()

    def get_custom(self, turn_data):
        ''' Game master provides a custom turn '''
        raise NotImplementedError()


class SysIO(AbstractIO):
    ''' Uses command line input for game flow '''
    def send(self, text):
        print('\n')
        for line in text.split('\n'):
            print(line)

        return {'success': True}

    def receive(self):
        print('\n')
        raw_response = input()
        return create_response(raw_response)

    def get_custom(self, turn):
        return {
            'text': ['I didn\'t catch that. Can you give me the letter of the option you wanted?'],
            'prompt': turn['prompt'],
            'options': [
                {'text': 'First option', 'destination': 'EXIT'},
                {'text': 'Second option', 'destination': None}
            ]
        }


class TwilioIO(AbstractIO):
    ''' connects to the twilio API '''

    def send(self, text):
        print(text)
        return {'success': True}


    def receive(self):
        # do nothing, wait for input
        time.sleep(3)
        return create_response('A')


    def get_custom(self, turn):
        return {
            'text': ['I didn\'t catch that. Can you give me the letter of the option you wanted?'],
            'prompt': turn['prompt'],
            'options': [
                {'text': 'First option', 'destination': 'EXIT'},
                {'text': 'Second option', 'destination': None}
            ]
        }
