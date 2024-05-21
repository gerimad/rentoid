from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, DecimalField
from wtforms.validators import DataRequired, InputRequired, NumberRange

class RatingForm(FlaskForm):
    score = DecimalField('What score would you give this flat? (1-10)', validators=[NumberRange(min=0, max=10, message="lba")])
    submit = SubmitField('Submit')