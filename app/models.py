from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager

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
    

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return f"<User {self.username}"

    @property
    def password(self):
        raise AttributeError('password is not readable')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))