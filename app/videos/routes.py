from flask import render_template, redirect, url_for, request, abort, flash
from ..models import Video, Review, TutorProfile
from . import videos
from ..extensions import db
from flask_login import current_user, login_required
from datetime import datetime as dt

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
    current_video = Video.query.get_or_404(video_id)
    current_video_url = current_video.youtube_url
    if current_video_url.startswith('https://www.youtube.com/watch?v='):
        VIDEO_ID = current_video_url.split("https://www.youtube.com/watch?v=")[1].split('&')[0]
    else:
        VIDEO_ID = current_video_url.split('https://youtu.be/')[1].split('?')[0]
    
    return render_template('videos/video.html', VIDEO_ID=VIDEO_ID, video=current_video)

@videos.route('/upload', methods=['POST', 'GET'])
@login_required
def upload_video():
    if not current_user.is_tutor:
        abort(403)
    else:
        if request.method == 'POST':
            tutor_id = current_user.tutor_profile.id
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

        return render_template('videos/upload.html')
    
@videos.route('/review/<int:video_id>', methods=["POST"])
@login_required
def review(video_id):
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
    print(video.tutor.avg_rating)

    video.tutor.avg_rating = avg_rating
    video.tutor.total_reviews = total_reviews
    db.session.commit()

    return redirect(url_for('videos.show_video', video_id= video_id))