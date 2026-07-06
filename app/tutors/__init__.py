from flask import Blueprint

tutors = Blueprint('tutors', __name__)

from . import routes