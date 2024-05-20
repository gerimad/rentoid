import os

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, InputRequired
from flask_sqlalchemy import SQLAlchemy

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from loading import SQLLoader
from scraping import Listing
from inference import InferenceEngine

infer = InferenceEngine()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dev-data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

app.config['SECRET_KEY'] = 'hard to guess string' #FIXME
bootstrap = Bootstrap(app)

class ListingForm(FlaskForm):
    text = StringField('Enter your listing here:', validators=[DataRequired()])
    submit = SubmitField('Summarize')


class RatingForm(FlaskForm):
    rating = RadioField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators=[InputRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def display_entries():
    listings = Flat.query.all()
    return render_template('entries.html', listings=listings)


@app.route('/summarise', methods=['GET','POST'])
def summariser():
    form = ListingForm()
    if form.validate_on_submit():
        old_text = session.get('text')
        flash('Submitted the listing succesfully!')
        session['text'] = infer.inference(form.text.data)
        return redirect(url_for('summariser'))
    return render_template('summariser.html', form=form, text=session.get('text'))

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    flats_df = pd.read_sql_table('flats', db.engine.connect())
    user_ratings_df = pd.read_sql_table('ratings', db.engine.connect())
    rated_flats_df = flats_df.merge(user_ratings_df, left_on='id', right_on='flat_id')
    
    scaler = MinMaxScaler()

    flats_df[['price', 'rooms', 'sqm']] = scaler.fit_transform(flats_df[['price', 'rooms', 'sqm']])
    rated_flats_df[['price', 'rooms', 'sqm']] = scaler.transform(rated_flats_df[['price', 'rooms', 'sqm']])

    weigthed_features = rated_flats_df[['price', 'rooms', 'sqm']].multiply(rated_flats_df['rating'], axis=0)
    user_profile = weigthed_features.sum(axis=0) / rated_flats_df['rating'].sum()

    flats_df['similarity'] = cosine_similarity(flats_df[['price', 'rooms', 'sqm']], [user_profile]).flatten()
    recommend_flats = flats_df.sort_values(by='similarity', ascending=False)
    print(recommend_flats[['similarity', 'id']])

    # FIXME id doesn't work for someresason
    flat_id = recommend_flats['id'].iloc[0]
    best = db.session.query(Flat).filter_by(id=int(flat_id)).one()
    summary = infer.inference(best.text)

    form = RatingForm()
    if form.validate_on_submit():
        old_rating = session.get('rating')
        flash('Submitted the rating succesfully!')

    return render_template('recommend.html', listing=summary, form=form)

if __name__ == '__main__':
    app.run(debug=True)