from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from ..models import TutorProfile, User, Purchase
from .helpers import tutor_required
from . import tutors
from ..extensions import db

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired #You can also add some length of characters


class ApplyForm(FlaskForm):
   bio = StringField('Bio', validators=[DataRequired()])
   courses = StringField('Courses', validators=[DataRequired()])


@tutors.route('/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    tutor = user.tutor_profile
    if tutor == None:
      abort(404)
    tutor_videos = user.tutor_profile.videos
    return render_template('tutors/index.html', videos=tutor_videos, tutor=tutor)


#Not rendering on the Home page
@tutors.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    apply_form = ApplyForm()
    tutor = TutorProfile.query.filter_by(user_id=current_user.id).first()
    if tutor:
        flash("You are already registered as a tutor")
        return render_template("tutors/apply.html", form=apply_form)
    if request.method == "POST":
        bio = apply_form.bio.data
        courses = apply_form.courses.data
  

        
        if apply_form.validate_on_submit():
          new_tutor = TutorProfile(
              bio=bio,
              courses=courses,
              user_id=current_user.id
              )
          
          db.session.add(new_tutor)
          db.session.commit()
          return redirect(url_for('main.home'))
    return render_template("tutors/apply.html", form=apply_form)


@tutors.route('/dashboard')
@login_required
@tutor_required
def dashboard():
    all_videos = current_user.tutor_profile.videos
    #Total earnings
    amount_paid = 0
    for video in all_videos:
      for p in video.purchase:
        amount_paid += p.amount_paid

    #Total views VIEW COUNT FEATURE YET TO BE IMPLEMENTED
    total_views = 0
    for video in all_videos:
        total_views += video.view_count

    #Total reviews
    total_reviews = 0
    for video in all_videos:
      total_reviews += len(video.reviews)

    return render_template('tutors/dashboard.html', AMOUNT_PAID=amount_paid, TOTAL_VIEWS=total_views, TOTAL_REVIEWS=total_reviews, ALL_VIDEOS=all_videos )

# dashboard()'s Python-loop aggregation (amount_paid, total_views, total_reviews) — flagged before, unchanged, still fine at your current scale, still worth converting to SQL aggregates eventually. Also still has the leftover