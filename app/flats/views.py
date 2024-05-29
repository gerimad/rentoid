from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import flats
from .forms import RatingForm
from ..llm.forms import SummariseForm
from .. import db
from ..model.models import Flat, FlatError, Rating
from ..llm.inference import InferenceEngine

@flats.route('/flat/<int:flat_id>', methods=["GET", "POST"])
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
    if form.submit.data and form.validate():
        summary = InferenceEngine.inference(flat.text)
        flash('Summary successfully created!', 'alert-success')

    if rating_form.submit.data and rating_form.validate():
        current_user.rate_flat(flat, rating_form.score.data)
        db.session.commit()
        flash('Submitted the rating succesfully!', 'alert-success')
    
    return render_template('flat.html', form=form, flat=flat, ratings=ratings, summary=summary, avg_rating = avg_score, my_rating=my_rating, rating_form=rating_form)

@flats.route('/all_flats')
@login_required
def all_flats():
    flats = Flat.get_all()
    return render_template('entries.html', flats = flats)

@flats.route('/like_flat/<int:flat_id>/<action>')
@login_required
def like_action(flat_id, action):
    flat = Flat.query.filter_by(id=flat_id).first_or_404()
    if action == 'like':
        current_user.like_flat(flat)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_flat(flat)
        db.session.commit()
    return redirect(url_for('flats.flat', flat_id=flat_id))