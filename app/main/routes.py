from flask_login import login_required, current_user
from flask import render_template, url_for, redirect
from ..models import TutorProfile, User
from . import main
from ..extensions import db


@main.route('/')
def home():
  
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    else:
        print("Hello World")
        print(current_user.is_authenticated)
        return render_template('main/home.html')
    

    #Work on the base.html template and include the navbar in the template.
