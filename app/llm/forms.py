from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, DecimalField
from wtforms.validators import DataRequired, InputRequired, NumberRange

class ListingForm(FlaskForm):
    text = StringField('Enter your listing here:', validators=[DataRequired()])
    submit = SubmitField('Summarize')


class SummariseForm(FlaskForm):
    submit = SubmitField('Create summary')
