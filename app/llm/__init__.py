from flask import Blueprint

llm = Blueprint('llm', __name__)

from . import views, forms, inference