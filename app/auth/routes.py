from flask import render_template, redirect, url_for, flash, request
from . import auth 
from ..extensions import db
from ..models import User, University
from werkzeug.security import generate_password_hash

from flask_login import login_user
from werkzeug.security import check_password_hash

from flask_login import logout_user, current_user



@auth.route('/register', methods=['GET', 'POST'])
def register():
    # LOGIC
    # GET request → show the form
    # POST request →
    # grab all form fields
    # check fields aren't empty → flash and redirect if so
    # check passwords match → flash and redirect if so
    # check email not already taken → flash and redirect if so
    # create user, commit, redirect to login
    # at the top of register() and login(), before anything else
    if current_user.is_authenticated:
        return redirect(url_for('videos.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        faculty = request.form.get('faculty')
        department = request.form.get('department')
        level = request.form.get('level')
        university_id = request.form.get('university_id')

        user = User.query.filter_by(email=email).first()

        if not email or not password or not full_name:
            flash('All fields are required.')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords must match')
            return redirect(url_for('auth.register'))
        

        if user:
            flash('Email already registered.')
            return redirect(url_for('auth.register'))

        
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            faculty=faculty,
            department=department,
            level=int(level),
            university_id=int(university_id),
            is_student=True,
            is_tutor=False,
            is_admin=False
        )
    

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    universities = University.query.all()
    return render_template('auth/register.html', universities=universities)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("videos.index"))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
        
        if not user:
            flash('No account found with that email')
            return redirect(url_for('auth.login'))
        
        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password. Please try again')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('videos.index'))
    
    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
        