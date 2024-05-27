from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from .forms import ListingForm, SummariseForm, RatingForm
from .. import db, infer
from ..models import Flat, Rating, Like, FlatError


import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

@main.route('/')
def index():
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
    text = None
    if form.validate_on_submit():
        flash('Submitted the listing succesfully!', 'alert-success')
        text = infer.inference(form.text.data).replace('\n', '<br>')
    return render_template('summariser.html', form=form, text=text)

@main.route('/flat/<int:flat_id>', methods=["GET", "POST"])
@login_required
def flat(flat_id):
    flat = Flat.query.filter_by(id=flat_id).first_or_404()
    ratings = Rating.query.filter_by(flat_id=flat_id).all()
    rating_form = RatingForm()

    my_rating = Rating.query.filter_by(flat_id=flat_id, user_id=current_user.id)
    if my_rating.count() == 1:
        my_rating = my_rating.first()
    else:
        my_rating = None

    try:
        avg_score = flat.average_rating()
    except FlatError as e:
        avg_score = None


    form = SummariseForm()
    summary = None
    if rating_form.submit.data and rating_form.validate():
        current_user.rate_flat(flat, rating_form.score.data)
        db.session.commit()
        flash('Submitted the rating succesfully!', 'alert-success')
        return redirect(f'{flat_id}')

    if form.submit.data and form.validate():
        summary = infer.inference(flat.text)
        flash('Summary successfully created!', 'alert-success')

    
    return render_template('flat.html', form=form, flat=flat, ratings=ratings, summary=summary, avg_rating = avg_score, my_rating=my_rating, rating_form=rating_form)

@main.route('/all_flats')
@login_required
def entries():
    flats = Flat.get_all()
    return render_template('entries.html', flats = flats)


@main.route('/like_flat/<int:flat_id>/<action>')
@login_required
def like_action(flat_id, action):
    flat = Flat.query.filter_by(id=flat_id).first_or_404()
    if action == 'like':
        current_user.like_flat(flat)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_flat(flat)
        db.session.commit()
    return redirect(url_for('main.flat', flat_id=flat_id))