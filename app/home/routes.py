from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, jsonify
from ..models import TutorProfile, User
from . import home
from ..extensions import db


@home.route('/')
def home():
  
    if not current_user.is_authenticated:
        # return redirect(url_for('auth.login'))
        return jsonify({'test':'The home route is working and the api wrappers is done'})
    
    else:
        return render_template('main/home.html')
    

    #Work on the base.html template and include the navbar in the template.
