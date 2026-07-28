from flask import render_template, redirect, url_for, request, abort, flash
from ..models import Video, Review, TutorProfile, Purchase
from flask import current_app
from . import videos
from ..extensions import db
from flask_login import current_user, login_required
from datetime import datetime as dt


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired #You can also add some length of characters


import os 
from dotenv import load_dotenv

import requests




class UploadVideoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    course_code = StringField('Course Code', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    youtube_url = StringField('Youtube URL', validators=[DataRequired()])
    price = FloatField('Price')

class ReviewForm(FlaskForm):
    comment = StringField('Leave a comment', validators=[DataRequired()])

class BuyForm(FlaskForm):
    pass

@videos.route('/')
@login_required
def index():
    course = request.args.get('course')

    if course:
        videos = Video.query.filter_by(course_code=course).all()
    else:
        videos = Video.query.all()

    return render_template('videos/index.html', videos=videos)

@videos.route('/show_video/<int:video_id>')
@login_required
#This isn't idiot proof😭
def show_video(video_id):
    review_form = ReviewForm()
    buy_form = BuyForm()
    current_video = Video.query.get_or_404(video_id)
    current_video_url = current_video.youtube_url
    if current_video_url.startswith('https://www.youtube.com/watch?v='):
        VIDEO_ID = current_video_url.split("https://www.youtube.com/watch?v=")[1].split('&')[0]
    else:
        VIDEO_ID = current_video_url.split('https://youtu.be/')[1].split('?')[0]
    if current_video.is_free:
        flash('the video is free so you can view it')
        if not current_user.id == current_video.tutor.user_id:
          current_video.view_count += 1
          db.session.commit()
        return render_template('videos/video.html', VIDEO_ID=VIDEO_ID, video=current_video)
    if Purchase.query.filter_by(student_id=current_user.id, video_id=video_id).first():
        flash('you bought the video you can view it')
        if not current_user.id == current_video.tutor.user.id:
          current_video.view_count += 1
          db.session.commit()
        return render_template('videos/video.html', VIDEO_ID=VIDEO_ID, video=current_video, review_form=review_form, buy_form=buy_form)# I need to get the buy button gated from those who have already paid
    if current_user.id == current_video.tutor.user_id:   
        flash('because you are the creator you can view it')
        return render_template('videos/video.html', VIDEO_ID=VIDEO_ID, video=current_video, review_form=review_form)
    else:
        flash('You cannot view this video without buying it')
        return render_template('videos/video.html', VIDEO_ID=0, video=current_video, review_form=review_form, buy_form=buy_form)

@videos.route('/upload', methods=['POST', 'GET'])
@login_required
def upload_video():
    if not current_user.is_tutor:
        abort(403)
    else:
        upload_video_form = UploadVideoForm()
        if request.method == 'POST':

            if upload_video_form.validate_on_submit():
            
              title = request.form.get('title')
              course_code = request.form.get('course_code')
              description = request.form.get('description')
              youtube_url = request.form.get('youtube_url')
              price = request.form.get('price')
              is_free = request.form.get('is_free') == 'True'
          
              new_video = Video(
                  tutor_id = current_user.tutor_profile.id,
                  title = title,
                  course_code = course_code,
                  description = description,
                  youtube_url = youtube_url,
                  created_at = dt.now(),
                  is_free = is_free,
                  price = price
                  
                  )
          
              db.session.add(new_video)
              db.session.commit()
              flash("VIDEO ADDED")
              return redirect(url_for('tutors.profile', user_id=current_user.id))

        return render_template('videos/upload.html', form=upload_video_form)
    
@videos.route('/review/<int:video_id>', methods=["POST"])
@login_required
def review(video_id):
    review_form = ReviewForm()
    video = Video.query.get(video_id)
    comment = request.form.get('comment')
    rating = request.form.get('rating')
    #Self check for video review
    if current_user.id == video.tutor.user_id:
        flash('You cannot review a video you own')
        return redirect(url_for('videos.show_video', video_id= video_id))
    
    #Duplicate check for video review
    existing = Review.query.filter_by(video_id=video_id, student_id=current_user.id).first()
    if existing:
        flash('You have already reviewed this video')
        return redirect(url_for('videos.show_video', video_id=video_id))
    if review_form.validate_on_submit():
      new_review = Review(
              video_id = video_id,
              student_id = current_user.id,
              rating = int(rating),
              comment = comment,
              created_at = dt.now()
          
          )
      db.session.add(new_review)
      db.session.flush()
      
      total_reviews = len(video.reviews)
      sum_rating = 0
      for review in video.reviews:
        sum_rating += review.rating 

      avg_rating = sum_rating/total_reviews

      video.tutor.avg_rating = avg_rating
      video.tutor.total_reviews = total_reviews
      db.session.commit()

      return redirect(url_for('videos.show_video', video_id= video_id, review_form=review_form))

@videos.route('<int:video_id>/buy', methods=["POST"])
@login_required
def buy(video_id):
    buy_form = BuyForm()
    PAYSTACK_API_TEST_PKEY = current_app.config['PAYSTACK_API_TEST_PKEY']
    PAYSTACK_API_TEST_SKEY = current_app.config['PAYSTACK_API_TEST_SKEY']
    # PAYSTACK_API_TEST_PKEY = os.environ.get("PAYSTACK_API_TEST_SKEY")
    header = {
        "Authorization": f"Bearer {PAYSTACK_API_TEST_SKEY}",
        "Content-Type": "application/json",
    }
    url = "https://api.paystack.co/transaction/initialize"
   
    price = Video.query.get(video_id).price
    price = float(price)
    #to change to KOBO
    price = price * 100
    email = current_user.email
    response = requests.post(url,
                         headers=header,
                         json={"email": email, 
                               "amount": price, 
                               "callback_url":url_for("videos.payment_callback", _external=True), 
                               "metadata": {
                                            "video_id": video_id}
                                }
                         )
    
    auth_url = response.json()['data']['authorization_url']
    return redirect(auth_url)


@videos.route('/payment/callback', methods=["GET"])
@login_required
def payment_callback():
    
    reference = request.args.get("reference")
    PAYSTACK_API_TEST_SKEY = current_app.config["PAYSTACK_API_TEST_SKEY"]
    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {PAYSTACK_API_TEST_SKEY}"}
    )
    
    data = response.json()

    if data['data']['status'] == 'success':
        amount_paid = data['data']['amount'] / 100
        video_id = data['data']['metadata']['video_id']

        new_purchase = Purchase(
            student_id=current_user.id,
            video_id=video_id,
            amount_paid=amount_paid,
            paystack_reference=reference,
            created_at=dt.now()
        )
        db.session.add(new_purchase)
        db.session.commit()

        flash('Payment successful! You now have access to this video.')
        return redirect(url_for('videos.show_video', video_id=video_id))
    
    else:
        flash('Payment failed. Please try again.')
        return redirect(url_for('videos.index'))


  
# Some things left to finish up:
# Review access gating
# Deleting of videos
# Updating description and prices of videos
# fixing the url for youtube not to break
# Fixing the buy button showing for a free video
