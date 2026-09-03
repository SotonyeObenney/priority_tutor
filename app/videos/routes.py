from flask import render_template, redirect, url_for, request, abort, flash, jsonify
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
        video_objects = Video.query.filter_by(course_code=course).all()

    else:
        video_objects = Video.query.all()

    # this search feature is broken it uses url parameters to work fix it
    # It looked explicitly for the search keywords and didn't return anything in general
    videos = [
        {
            "id": v.id,
            "title": v.title,
            "course_code": v.course_code,
            "price": v.price,
            "is_free": v.is_free,
            "view_count": v.view_count,
        }
        for v in video_objects
    ]

    return jsonify({"videos": videos}), 200


@videos.route('/show_video/<int:video_id>')
@login_required
def show_video(video_id):
    current_video = Video.query.get_or_404(video_id)
    current_video_url = current_video.youtube_url
    VIDEO_ID = extract_video_id(current_video_url)
    
    video_access, owner, message = can_access_video(current_user, current_video)
    if not video_access:
      return jsonify({"message": "You must buy this video to watch it"}), 402

    current_video.view_count += 1
    db.session.commit()
    return jsonify({'message': message, 'video': {
        'id': current_video.id,
        'is_owner': owner,
        'price' : current_video.price,
        'title': current_video.title,
        'course_code': current_video.course_code,
        'description': current_video.description,
        'tutor' : current_video.tutor.user.full_name,
        'VIDEO_ID': VIDEO_ID
    }
       }), 200
    






@videos.route('/upload', methods=['POST'])
@login_required
@tutor_required
def upload_video():
    upload_video_form = UploadVideoForm()
    data = request.get_json(silent=True)

    if not data:
      return jsonify({"error": "Invalid or missing JSON body"}), 400

    
    if upload_video_form.validate_on_submit():
      title = data.get('title')
      course_code = data.get('course_code')
      description = data.get('description')
      youtube_url = data.get('youtube_url')
      price = data.get('price')
      is_free = data.get('is_free') == 'True'
      #is free should cancel out price from getting filled
      
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
      return jsonify({"message": "Video Uploaded Successfully"}), 201
    else:
        return jsonify({'error': upload_video_form.errors}), 400
  
@videos.route('/review/<int:video_id>', methods=["POST"])
@login_required
def review(video_id):
    review_form = ReviewForm()
    data = request.get_json(silent=True)

    if not data:
      return jsonify({"error": "Invalid or missing JSON body"}), 400

    current_video = Video.query.get_or_404(video_id)
    comment = data.get('comment')
    rating = data.get('rating')
    video_access, owner, message = can_access_video(current_user, current_video)
    if not video_access:
        return jsonify({'message': message}), 403
    if owner:
        return jsonify({'message': message}), 403
        
    
    existing = Review.query.filter_by(video_id=video_id, student_id=current_user.id).first()
    if existing:
      return jsonify({'message': 'You have already reviewed this video'}), 409

    if review_form.validate_on_submit():
      new_review = Review(
              video_id = video_id,
              student_id = current_user.id,
              rating = int(rating),
              comment = comment          
          )
      db.session.add(new_review)
      db.session.commit()
      recalculate_tutor_rating(current_video, db)

      return jsonify({'message': 'Review successfully made'}), 201

    else:
      return jsonify({'errors': review_form.errors}), 400

    
    


@videos.route('/buy/<int:video_id>')
@login_required
def buy(video_id):
    if Purchase.query.filter_by(student_id=current_user.id, video_id=video_id).first():
      return jsonify({'error':'You have already purchased this video'}),403
    
    current_video = Video.query.get_or_404(video_id)

    amount = float(current_video.price)
    amount *= 100
    email = current_user.email
    callback_url = url_for('videos.show_video', video_id=video_id)
    metadata = {"video_id": video_id,
                "student_id": current_user.id
                }

    auth_url = initialize_transaction(email, amount, callback_url, metadata)

    if auth_url:
      return jsonify({'message': "Payment Initialization successful",
                      'auth_url': auth_url
                      }), 200

    else:
      return jsonify({'message': "Payment Initialization failed"}), 500


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
  return redirect(url_for('videos.show_video', video_id=video_id))#This will connect with my react front end



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