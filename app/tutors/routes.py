from flask import render_template
from . import tutors

@tutors.route('/tutors')
def index():
    return render_template('tutors/index.html')