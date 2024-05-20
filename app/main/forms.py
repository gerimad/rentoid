from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired, InputRequired

class ListingForm(FlaskForm):
    text = StringField('Enter your listing here:', validators=[DataRequired()])
    submit = SubmitField('Summarize')

class RatingForm(FlaskForm):
    rating = RadioField('Rating', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], validators=[InputRequired()])
    submit = SubmitField('Submit')