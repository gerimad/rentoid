from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from ..model.models import Flat

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





