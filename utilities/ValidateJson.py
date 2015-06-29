''' Checks if the game json file will produce a valid graph '''
import json
import logging
import sys

def validate(turns):
    ''' check if the json file will work '''
    turn_uids = []
    for turn in turns:
        if not ('id' in turn and 'text' in turn and 'options' in turn):
            logging.error('fields missing in turn %s', json.dumps(turn))

        if not isinstance(turn['text'], list):
            logging.error('text should be a list for turn %s', json.dumps(turn))

        if turn['id'] in turn_uids:
            logging.error('duplicate turn uid %s', turn['id'])

        for text in turn['text']:
            if len(text) > 140:
                logging.warn('Turn %s too long', turn['id'])

        turn_uids.append(turn['id'])

    for turn in FILE:
        for option in turn['options']:
            if not ('text' in option and 'destination' in option):
                logging.error('fields missing from option %s', json.dumps(turn))

            if not option['destination'] in turn_uids:
                logging.error('unknown destination %s in turn %s', json.dumps(option), turn['id'])

if __name__ == '__main__':
    FILE = json.load(open(sys.argv[1], 'r'))
    validate(FILE)
