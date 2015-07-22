''' The interface for performing I/O to the player '''
import time

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
        return raw_response

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
        # do nothing, wait for webhook
        time.sleep(3)
        return 'A'


    def get_custom(self, turn):
        return {
            'text': ['I didn\'t catch that. Can you give me the letter of the option you wanted?'],
            'prompt': turn['prompt'],
            'options': [
                {'text': 'First option', 'destination': 'EXIT'},
                {'text': 'Second option', 'destination': None}
            ]
        }
