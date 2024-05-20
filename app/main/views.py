from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import ListingForm, RatingForm
from .. import db, infer
from ..models import Flat


import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

@main.route('/')
def index():
    listings = Flat.query.all()
    print(len(listings))
    return render_template('entries.html', listings=listings)

@main.route('/summarise', methods=['GET','POST'])
def summarise():
    form = ListingForm()
    if form.validate_on_submit():
        old_text = session.get('text')
        flash('Submitted the listing succesfully!')
        session['text'] = infer.inference(form.text.data)
        return redirect(url_for('.summarise'))
    return render_template('summariser.html', form=form, text=session.get('text'))


@main.route('/recommend', methods=['GET', 'POST'])
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