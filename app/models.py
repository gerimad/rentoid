from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class Flat(db.Model):
    __tablename__ = 'flats'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    sqm = db.Column(db.Integer)
    rooms = db.Column(db.Numeric)
    location = db.Column(db.Text)
    text = db.Column(db.Text)
    link = db.Column(db.String)

    def __repr__(self):
        return f'<Flat id:#{self.id}>'
    
    def __str__(self):
        return f'ID: {self.id}\nPrice: {self.price}\nSQM: {self.sqm}\n# of rooms: {self.rooms}\nLocation: {self.location}\nText: {self.text}\nLink: {self.link}'

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    flat_id = db.Column(db.Integer, db.ForeignKey('flats.id'))
    rating = db.Column(db.Float)

    def __repr__(self):
        return f"<Rating flat:{self.flat_id} rating:{self.rating}>"