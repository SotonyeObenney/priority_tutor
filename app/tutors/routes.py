from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models import TutorProfile, User, Purchase
from . import tutors
from ..extensions import db


@tutors.route('/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    tutor = user.tutor_profile
    tutor_videos = user.tutor_profile.videos
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


@tutors.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_tutor:
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

      print(total_views)


      #Total reviews
      total_reviews = 0
      for video in all_videos:
        total_reviews += len(video.reviews)

     
      


      return render_template('tutors/dashboard.html', AMOUNT_PAID=amount_paid, TOTAL_VIEWS=total_views, TOTAL_REVIEWS=total_reviews, ALL_VIDEOS=all_videos )
    else:
      return render_template('error.html')

    