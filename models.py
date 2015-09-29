''' Defines a postgres model to store game data '''
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Player(db.Model):
    ''' records of players '''
    __tablename__ = 'player'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    name = db.Column(db.String)
    phone = db.Column(db.String(11), unique=True)
    contacted = db.Column(db.Boolean, default=False)
    show = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    pending_turn = db.Column(JSON)
    messages = db.relationship('Message', backref='Player', lazy='dynamic')

    def __init__(self, name, number):
        self.name = name
        self.phone = number

    def serialize(self):
        ''' make it json-able '''
        messages = self.messages

        message_data = []
        try:
            for message in messages:
                message_data.append(message.serialize())
        except:
            pass

        data = {
            'created': self.created.isoformat(),
            'name': self.name,
            'phone': self.phone,
            'notes': self.notes if self.notes else '',
            'pending_turn': self.pending_turn,
            'show': self.show,
            'messages': message_data
        }
        return data


    def save(self):
        ''' add a new player '''
        db.session.add(self)
        db.session.commit()
        return self


    def set_pending_turn(self, turn_data):
        ''' set the pending turn in the database '''
        self.pending_turn = turn_data
        self.save()
        return self


    def toggle_show(self):
        ''' show or hide a player '''
        self.show = not self.show
        db.session.commit()
        return self


def find_player(phone):
    ''' looks up a player by phone number '''
    return db.session.query(Player).filter(Player.phone == phone).one()


def get_uncontacted_player():
    ''' get an uncontacted player '''
    return db.session.query(Player).filter(Player.contacted == False).one()

def add_player(name, phone):
    ''' add a new player '''
    player = Player(name, phone)
    player.save()
    return player


class Message(db.Model):
    ''' messages exchanged '''
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    player = db.Column(db.Integer, db.ForeignKey('player.id'))
    sms_data = db.Column(JSON)
    turn_data = db.Column(JSON)
    text = db.Column(db.Text)
    incoming = db.Column(db.Boolean, default=False)

    def __init__(self, player_id, sms_data, turn_data, incoming):
        self.player = player_id
        self.sms_data = sms_data
        self.turn_data = turn_data
        self.incoming = incoming


    def serialize(self):
        ''' make it json-able '''
        data = {
            'created': self.created.isoformat(),
            'turn_data': self.turn_data,
            'incoming': self.incoming
        }
        return data


def add_message(player, turn_data, sms, incoming=False):
    ''' log a turn in the database '''
    message = Message(player.id, turn_data, sms, incoming)
    db.session.add(message)
    db.session.commit()
    return message

