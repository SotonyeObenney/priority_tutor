from flask import render_template, redirect, url_for, request
from ..models import Video
from . import videos

from flask_login import current_user, login_required


@videos.route('/')
@login_required
def index():
    course = request.args.get('course')
    print(course)
    if course:
        videos = Video.query.filter_by(course_code=course).all()
    else:
        videos = Video.query.all()
        print("all of them")

    return render_template('videos/index.html', videos=videos)

@videos.route('/show_video/<int:video_id>')
@login_required
def show_video(video_id):
    current_video = Video.query.get_or_404(video_id)
    current_video_url = current_video.youtube_url
    if current_video_url.startswith('https://www.youtube.com/watch?v='):
        VIDEO_ID = current_video_url.split("https://www.youtube.com/watch?v=")[1].split('&')[0]
    else:
        VIDEO_ID = current_video_url.split('https://youtu.be/')[1].split('?')[0]
    print(VIDEO_ID)
    
    return render_template('videos/video.html', VIDEO_ID=VIDEO_ID, video=current_video)

