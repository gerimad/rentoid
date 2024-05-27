from flask import render_template, redirect, url_for, flash
from . import llm
from .forms import ListingForm
from .. import infer

@llm.route('/summarise', methods=['GET','POST'])
def summarise():
    form = ListingForm()
    text = None
    if form.validate_on_submit():
        flash('Submitted the listing succesfully!', 'alert-success')
        text = infer.inference(form.text.data).replace('\n', '<br>')
    return render_template('summariser.html', form=form, text=text)