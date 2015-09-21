''' Defines a postgres model to store game data '''
from WebRunner import db
from sqlalchemy.dialects.postgresql import JSON

class Player(db.Model):
    ''' Game data on a per-player basis '''
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(11), unique=True)
    turn_history = db.Column(JSON)
    current_turn = db.Column(JSON)
    start_time = db.Column(db.DateTime, server_default=db.func.now())
    show = db.Column(db.Boolean)

    def __init__(self, name, number):
        self.name = name
        self.phone = number
        self.turn_history = []

    def __repr__(self):
        return '<id {}>'.format(self.id)
