from flask import render_template
from . import videos

@videos.route('/')
def index():
    return render_template('videos/index.html')