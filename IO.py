''' The interface for performing I/O to the player '''
import configparser
import logging
import time
from twilio.rest import TwilioRestClient

class AbstractIO(object):
    ''' Defines basic types of communication (in and out) '''

    def send(self, text, recipient):
        ''' Prompt the player with a scene or options '''
        raise NotImplementedError()

    def receive(self):
        ''' Get an answer from the player '''
        raise NotImplementedError()


class SysIO(AbstractIO):
    ''' Uses command line input for game flow '''
    def send(self, text, recipient=None):
        print('\n')
        for line in text.split('\n'):
            print(line)

        return {'success': True}

    def receive(self):
        print('\n')
        raw_response = input()
        return raw_response


class TwilioIO(AbstractIO):
    ''' connects to the twilio API '''

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('settings.ini')
        if config['environment']['debug']:
            config.read('dev-settings.ini')
        else:
            config.read('prod-settings.ini')

        try:
            twilio_config = config['twilio']
        except KeyError:
            logging.error('Missing twilio config settings')
        else:
            try:
                account_sid = twilio_config['account_sid']
                auth_token = twilio_config['auth_token']
                self.client = TwilioRestClient(account_sid, auth_token)
                self.sender = twilio_config['sender']

            except KeyError:
                logging.error('Missing auth_sid or auth_token in twilio config')


    def send(self, text, recipient):
        try:
            message = self.client.messages.create(body=text, to=recipient, from_=self.sender)
        except AttributeError:
            logging.error('Twilio client not found')
            return False

        logging.info('Sent message to recipient %s: %s', recipient, text)
        message = {
            'date_updated': message.date_updated.isoformat() if message.date_updated else '',
            'date_sent': message.date_sent.isoformat() if message.date_sent else '',
            'date_created': message.date_created.isoformat() if message.date_created else '',
            'status': message.status,
            'from': message.from_,
            'direction': message.direction,
            'to': message.to,
            'sid': message.sid,
            'body': message.body
        }
        return message


    def receive(self):
        return 'A'
