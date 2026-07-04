from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import TutorProfile, User
from . import tutors
from ..extensions import db


@tutors.route('/<int:user_id>')
@login_required
def profile(user_id):
    tutor = TutorProfile.query.get_or_404(user_id)
    tutor_videos = tutor.videos
    print(tutor_videos)
    return render_template('tutors/index.html', videos=tutor_videos, tutor=tutor)


#Not rendering on the Home page
@tutors.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if request.method == "POST":
        bio = request.form.get('bio')
        courses = request.form.get('courses')
        user_id = current_user.id

        tutor = TutorProfile.query.filter_by(user_id=user_id).first()
        if tutor:
            flash("You are already registered as a tutor")
            return render_template("tutors/apply.html")
        
        new_tutor = TutorProfile(
            bio=bio,
            courses=courses,
            user_id=current_user.id
            )
        
        db.session.add(new_tutor)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template("tutors/apply.html")
