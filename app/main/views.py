from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import main
from ..model.models import Flat

@main.route('/')
def index():
    liked_flats = None
    rated_flats = None

    if current_user.is_authenticated:
        rated_flats = current_user.rated.all()
        liked_flats = current_user.liked.all()

    return render_template('index.html', liked_flats=liked_flats, rated_flats=rated_flats)
