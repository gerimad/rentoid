from flask import Blueprint

flats = Blueprint('flats', __name__)

from . import views, forms