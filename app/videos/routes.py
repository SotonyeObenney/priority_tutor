from flask import render_template, redirect, url_for, request, abort, flash
from ..models import Video, Review, TutorProfile, Purchase
from flask import current_app
from . import videos
from ..extensions import db
from flask_login import current_user, login_required
from datetime import datetime as dt
import requests
from ..tutors.helpers import tutor_required

import hmac
import hashlib

from .helpers import can_access_video, extract_video_id, recalculate_tutor_rating
from .paystack import initialize_transaction, verify_transaction, record_purchase


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired #You can also add some length of characters

from functools import wraps

import os 
from dotenv import load_dotenv







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
def show_video(video_id):
    review_form = ReviewForm()
    buy_form = BuyForm()
    current_video = Video.query.get_or_404(video_id)
    current_video_url = current_video.youtube_url
    VIDEO_ID = extract_video_id(current_video_url)
    
    video_access, owner = can_access_video(current_user, current_video)
    if not video_access:
      flash("You must buy this video to watch it") 
    return render_template('videos/video.html', VIDEO_ID=VIDEO_ID, ACCESS=video_access, OWNER=owner, video=current_video, review_form=review_form, buy_form=buy_form)





@videos.route('/upload', methods=['POST', 'GET'])
@login_required
@tutor_required
def upload_video():
    upload_video_form = UploadVideoForm()
    if request.method == 'POST':
        if upload_video_form.validate_on_submit():
          title = upload_video_form.title.data
          course_code = upload_video_form.course_code.data
          description = upload_video_form.description.data
          youtube_url = upload_video_form.youtube_url.data
          price = upload_video_form.price.data
          is_free = request.form.get('is_free')== 'True'
      
          new_video = Video(
              tutor_id = current_user.tutor_profile.id,
              title = title,
              course_code = course_code,
              description = description,
              youtube_url = youtube_url,
              is_free = is_free,
              price = price
              
              )
          db.session.add(new_video)
          db.session.commit()
          flash("VIDEO ADDED")
          return redirect(url_for('tutors.profile', user_id=current_user.id))
        else:
            flash(upload_video_form.errors)
            pass
    return render_template('videos/upload.html', form=upload_video_form)
  
@videos.route('/review/<int:video_id>', methods=["POST"])
@login_required
def review(video_id):
    review_form = ReviewForm()
    current_video = Video.query.get_or_404(video_id)
    comment = request.form.get('comment')
    rating = request.form.get('rating')
    video_access, owner = can_access_video(current_user, current_video)
    if not video_access:
        flash('You must have access to this video before reviewing it')
        return redirect(url_for('videos.show_video', video_id=video_id))
    if owner:
        flash('You cannot review a video you own')
        return redirect(url_for('videos.show_video', video_id= video_id))
    
    existing = Review.query.filter_by(video_id=video_id, student_id=current_user.id).first()
    if existing:
        flash('You have already reviewed this video')
        return redirect(url_for('videos.show_video', video_id=video_id))
    if review_form.validate_on_submit():
      new_review = Review(
              video_id = video_id,
              student_id = current_user.id,
              rating = int(rating),
              comment = comment          
          )
      db.session.add(new_review)
      db.session.commit()

      flash("Review succesfully added")
      recalculate_tutor_rating(current_video, db)
      # db.session.commit()
    else:
      flash(review_form.errors)
      return redirect(url_for('videos.show_video', video_id= video_id, review_form=review_form))
    
    
    return redirect(url_for('videos.show_video', video_id= video_id, review_form=review_form))

@videos.route('/buy/<int:video_id>', methods=["POST"])
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

    
    amount = float(Video.query.get_or_404(video_id).price)
    amount *= 100
    email = current_user.email
    callback_url = url_for('videos.show_video', video_id=video_id)
    metadata = {"video_id": video_id,
                "student_id": current_user.id
                }


    auth_url = initialize_transaction(email, amount, callback_url, metadata)

    if auth_url:
      return redirect(auth_url)
    else:
      return redirect(url_for('videos.show_video', video_id=video_id))


@videos.route('/payment/callback', methods=["GET"])
@login_required
def payment_callback():
  reference = request.args.get("reference")
  data = verify_transaction(reference)

  if not data or not data.get('data') or data['data'].get('status') != 'success':
    flash('Payment could not be verified. Please try again.')
    return redirect(url_for('videos.index'))

  
  video_id = data['data']['metadata']['video_id']
  flash("Payment received! We're confirming it now — this can take a few seconds.")
  return redirect(url_for('videos.show_video', video_id=video_id))



@videos.route('/payment_webhook', methods=['POST'])
def handle_paystack_webhook():
    PAYSTACK_API_TEST_SKEY = current_app.config["PAYSTACK_API_TEST_SKEY"]   
    paystack_signature = request.headers.get('x-paystack-signature')
    if not paystack_signature:
        abort(401)


    raw_payload = request.get_data()
    computed_hash = hmac.new(
        key=PAYSTACK_API_TEST_SKEY.encode('utf-8'),
        msg=raw_payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    if hmac.compare_digest(computed_hash, paystack_signature):

      payload = request.get_json()
      reference = payload['data']['reference']
      
      data = verify_transaction(reference)

      if not data or not data.get('data') or data['data'].get('status') != 'success':
        abort(400)
    
      if data['data']['status'] == 'success':
          amount_paid = data['data']['amount'] / 100
          video_id = data['data']['metadata']['video_id']
          student_id = data['data']['metadata']['student_id']
          amount_paid = data['data']['amount'] / 100
          record_purchase(student_id, video_id, amount_paid, reference, db)    
      return "OK", 200
    else:
      abort(400)


    


  
# Some things left to finish up:
# Review access gating
# Deleting of videos
# Updating description and prices of videos
# fixing the url for youtube not to break
# Fixing the buy button showing for a free video
# Webhooks
#What to do when network is down on the payment gateway
#I allowed creators to leave reviews on their own videos
#Video.query.paginate(...) for index route