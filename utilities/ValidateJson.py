''' Checks if the game json file will produce a valid graph '''
import json
import sys

def validate(turns):
    ''' check if the json file will work '''
    turn_uids = []
    for turn in turns:
        if not ('id' in turn and 'text' in turn and 'options' in turn):
            return 'fields missing in turn %s' % json.dumps(turn)

        if not isinstance(turn['text'], list):
            return 'text should be a list for turn %s' % json.dumps(turn)

        if turn['id'] in turn_uids:
            return 'duplicate turn uid %s' % turn['id']

        turn_uids.append(turn['id'])

    for turn in FILE:
        for option in turn['options']:
            if not ('text' in option and 'destination' in option):
                return 'fields missing from option %s' % json.dumps(turn)

            if not option['destination'] in turn_uids:
                return 'unknown destination %s in turn %s' % (json.dumps(option), turn['id'])

    return 'SUCCESS: valid file'

if __name__ == '__main__':
    FILE = json.load(open(sys.argv[1], 'r'))
    print validate(FILE)
