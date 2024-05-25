from flask_login import current_user, login_required
from flask import redirect, request, flash, session, render_template, url_for
from .. import db, infer
from . import recommender
from .forms import RatingForm
from ..main.forms import SummariseForm
from ..models import Flat, Rating


@recommender.route('/recommend', methods=['GET', 'POST'])
@login_required
def recommend():
    best_flat = current_user.get_best_flat()
    form = RatingForm()
    form2 = SummariseForm()

    summary = None
    if form.submit.data and form.validate():
        current_user.rate_flat(best_flat, form.score.data)
        db.session.commit()
        flash('Submitted the rating succesfully!')
        return redirect(url_for('.recommend'))

    if form2.submit.data and form2.validate():
        summary = infer.inference(best_flat.text)
        flash('Summary created!')
        #return redirect(url_for('.recommend'))


    return render_template('recommend.html', summary=summary, form=form, form2=form2, flat=best_flat)
    

# @recommender.route('/rate/<int:flat_id>/<float:score>')
# @login_required
# def rate_flat(flat_id, score):
#     flat = Flat.query.filter_by(id=flat_id).first()
#     current_user.rate_flat(flat, score)
#     db.session.commit()
#     return redirect(request.referrer)


@recommender.route('/like/<int:flat_id>/<action>')
@login_required
def like_action(flat_id, action):
    flat = Flat.query.filter_by(id=flat_id).first_or_404()
    if action == 'like':
        current_user.like_flat(flat)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_flat(flat)
        db.session.commit()
    return redirect(url_for('.recommend'))
