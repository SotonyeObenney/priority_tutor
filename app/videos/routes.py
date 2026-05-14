from flask import render_template, redirect, url_for
from ..models import Video
from . import videos

from flask_login import current_user, login_required


@videos.route('/')
@login_required
def index():
    # if not current_user.is_authenticated:
    #     return redirect(url_for('auth.login')) use @login_required instead
    
    videos = Video.query.all() # can you explain how this works and also the other things I can do with query.
                               #What exactly is query in just regular python like how it's used here

    return render_template('videos/index.html', videos=videos)