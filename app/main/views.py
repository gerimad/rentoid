from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from .forms import ListingForm, RatingForm, SummariseForm
from .. import db, infer
from ..models import Flat, Rating, Like


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
        flash('Submitted the listing succesfully!')
        text = infer.inference(form.text.data).replace('\n', '<br>')
    return render_template('summariser.html', form=form, text=text)

@main.route('/flat/<int:flat_id>', methods=["GET", "POST"])
def flat(flat_id):
    flat = Flat.query.filter_by(id=flat_id).first()
    ratings = Rating.query.filter_by(flat_id=flat_id).all()

    form = SummariseForm()
    summary = None
    if form.validate_on_submit():
        summary = infer.inference(flat.text)
        flash('Summary successfully created!')
    
    return render_template('flat.html', form=form, flat=flat, ratings=ratings, summary=summary)