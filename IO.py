''' The interface for performing I/O to the player '''

class AbstractIO(object):
    ''' Defines basic types of communication (in and out) '''

    def send(self, text):
        ''' Prompt the player with a scene or options '''
        raise NotImplementedError()

    def receive(self):
        ''' Get an answer from the player '''
        raise NotImplementedError()

class SysIO(AbstractIO):
    ''' Uses command line input for game flow '''
    def send(self, text):
        print text

    def receive(self):
        return raw_input()

