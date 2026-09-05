from flask import Blueprint

home = Blueprint('main', __name__)

from . import routes