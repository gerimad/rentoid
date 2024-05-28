from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import jsonify
from sqlalchemy import func
from .. import db, login_manager

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

class FlatError(Exception):
    def __init__(self, message="An error occurred in the Flat class"):
        self.message = message
        super().__init__(self.message)

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
    
    def average_rating(self):
        ratings = Rating.query.filter_by(flat_id = self.id)
        if ratings.count() == 0:
            raise FlatError(f"Flat {self.id} has no ratings")
        else:
            avg_score = ratings.with_entities(func.avg(Rating.rating)).scalar()
            return avg_score
    
    @classmethod
    def get_all(cls):
        return cls.query.all()

class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    flat_id = db.Column(db.Integer, db.ForeignKey('flats.id'))
    rating = db.Column(db.Float)

    __table_args__ = (db.UniqueConstraint('user_id', 'flat_id', name='unique_user_flat_rating'),)

    def __repr__(self):
        return f"<Rating flat: {self.flat_id} by user: {self.user_id}>"
    
    
    def get_author(self):
        return User.query.filter_by(id=self.user_id).first().username

class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    flat_id = db.Column(db.Integer, db.ForeignKey('flats.id'))

    __table_args__ = (db.UniqueConstraint('user_id', 'flat_id', name='unique_user_flat_like'),)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    liked = db.relationship('Like', foreign_keys='Like.user_id', backref='user', lazy='dynamic')
    rated = db.relationship('Rating', foreign_keys='Rating.user_id', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        raise AttributeError('password is not readable')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_liked_flat(self, flat):
        return Like.query.filter(Like.user_id == self.id, Like.flat_id == flat.id).count() > 0

    def like_flat(self, flat):
        if not self.has_liked_flat(flat):
            like = Like(user_id=self.id, flat_id=flat.id)
            db.session.add(like)

    def unlike_flat(self, flat):
        if self.has_liked_flat(flat):
            Like.query.filter_by(user_id=self.id, flat_id=flat.id).delete()
    
    def has_rated_flat(self, flat):
        return Rating.query.filter(Rating.user_id == self.id, Rating.flat_id == flat.id).count() > 0
    
    def rate_flat(self, flat, score):
        if not self.has_rated_flat(flat):
            rating = Rating(user_id = self.id, flat_id = flat.id, rating=score)
            db.session.add(rating)
        else:
            rating = Rating.query.filter_by(flat_id=flat.id, user_id=self.id).first()
            rating.rating = score
            db.session.add(rating)

    def get_best_flat(self):
        if self.rated.count() == 0:
            return Flat.query.first()

        joined_table = db.session.query(Flat, Rating) \
            .join(Rating, Flat.id == Rating.flat_id) \
            .filter_by(user_id=self.id).all()

        rated_data = [(flat.id, flat.price, flat.rooms, flat.sqm, rating.rating) for flat, rating in joined_table]
        rated_flats = pd.DataFrame(rated_data, columns=['flat_id', 'price', 'rooms', 'sqm', 'rating'])

        flats_table = db.session.query(Flat).all()
        flats_data = [(flat.id, flat.price, flat.rooms, flat.sqm) for flat in flats_table]
        flats  = pd.DataFrame(flats_data, columns=['flat_id', 'price', 'rooms', 'sqm'])


        best_flat_id = self.compute_best_flat(rated_flats, flats)

        best = db.session.query(Flat).filter_by(id=int(best_flat_id)).first()
        return best
    
    @staticmethod
    def compute_best_flat(rated_flats, flats):
        scaler = MinMaxScaler()
        features = ['price', 'rooms', 'sqm']

        flats[features] = scaler.fit_transform(flats[features])
        rated_flats[features] = scaler.transform(rated_flats[features])

        weighted_features = rated_flats[features].multiply(rated_flats['rating'], axis=0)
        user_profile = weighted_features.sum(axis=0) / rated_flats['rating'].sum()
        
        flats['similarity'] = cosine_similarity(flats[features], [user_profile]).flatten()

        merged = flats.merge(rated_flats, on='flat_id', how='left', indicator=True)
        unrated_flats = merged[merged['_merge'] == 'left_only']
        unrated_flats = unrated_flats.drop(columns=['_merge'])

        recommended_flats = unrated_flats.sort_values(by='similarity', ascending=False)
        best_flat_id = recommended_flats['flat_id'].iloc[0]

        return best_flat_id

    
    def get_rating(self, flat):
        if self.has_rated_flat():
            return self.rated.filter_by(flat_id=flat.id).first().rating 
        else:
            raise ValueError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))