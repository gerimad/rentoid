from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from .forms import ListingForm, RatingForm
from .. import db, infer
from ..models import Flat, Rating, Like


import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

@main.route('/')
def index():
    # listings = Flat.query.all()
    # print(len(listings))
    # return render_template('entries.html', listings=listings)
    liked_flats = None
    rated_flats = None

    if current_user.is_authenticated:
        liked_flat_ids = [like.flat_id for like in current_user.liked.all()]
        rated_flat_ids = [rating.flat_id for rating in current_user.rated.all()]

        rated_flats = Flat.query.filter(Flat.id.in_(rated_flat_ids)).all()
        liked_flats = Flat.query.filter(Flat.id.in_(liked_flat_ids)).all()

    return render_template('index.html', liked_flats=liked_flats, rated_flats=rated_flats)

@main.route('/summarise', methods=['GET','POST'])
def summarise():
    form = ListingForm()
    if form.validate_on_submit():
        old_text = session.get('text')
        flash('Submitted the listing succesfully!')
        session['text'] = infer.inference(form.text.data)
        return redirect(url_for('.summarise'))
    return render_template('summariser.html', form=form, text=session.get('text'))

@main.route('/flat/<int:flat_id>')
def flat(flat_id):
    flat = Flat.query.filter_by(id=flat_id).first()
    return render_template('flat.html', flat=flat)


# @main.route('/recommend', methods=['GET', 'POST'])
# @login_required
# def recommend():
#     flats_df = pd.read_sql_table('flats', db.engine.connect())
#     user_ratings_df = pd.read_sql_table('ratings', db.engine.connect())
#     rated_flats_df = flats_df.merge(user_ratings_df, left_on='id', right_on='flat_id')
    
#     scaler = MinMaxScaler()

#     flats_df[['price', 'rooms', 'sqm']] = scaler.fit_transform(flats_df[['price', 'rooms', 'sqm']])
#     rated_flats_df[['price', 'rooms', 'sqm']] = scaler.transform(rated_flats_df[['price', 'rooms', 'sqm']])

#     weigthed_features = rated_flats_df[['price', 'rooms', 'sqm']].multiply(rated_flats_df['rating'], axis=0)
#     user_profile = weigthed_features.sum(axis=0) / rated_flats_df['rating'].sum()

#     flats_df['similarity'] = cosine_similarity(flats_df[['price', 'rooms', 'sqm']], [user_profile]).flatten()
#     recommend_flats = flats_df.sort_values(by='similarity', ascending=False)
#     print(recommend_flats[['similarity', 'id']])

#     flat_id = recommend_flats['id'].iloc[0]
#     best = db.session.query(Flat).filter_by(id=int(flat_id)).first()
#     summary = infer.inference(best.text)

#     form = RatingForm()
#     if form.validate_on_submit():
#         old_rating = session.get('rating')
#         flash('Submitted the rating succesfully!')

#     return render_template('recommend.html', flat=best, summary=summary, form=form)


# @main.route('/like/<int:flat_id>/<action>')
# @login_required
# def like_action(flat_id, action):
#     flat = Flat.query.filter_by(id=flat_id).first_or_404()
#     if action == 'like':
#         current_user.like_flat(flat)
#         db.session.commit()
#     if action == 'unlike':
#         current_user.unlike_flat(flat)
#         db.session.commit()
#     return redirect(request.referrer)