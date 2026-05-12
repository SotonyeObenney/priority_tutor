from flask import Blueprint

videos = Blueprint('videos', __name__)

from . import routes