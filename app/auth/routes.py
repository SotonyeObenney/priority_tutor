from flask import render_template, redirect, url_for, flash, request
from . import auth 
from ..extensions import db
from ..models import User, University
from werkzeug.security import generate_password_hash

from flask_login import login_user
from werkzeug.security import check_password_hash

from flask_login import logout_user


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        faculty = request.form.get('faculty')
        department = request.form.get('department')
        level = request.form.get('level')
        university_id = request.form.get('university_id')

        user = User.query.filter_by(email=email).first()

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
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
        
        if not user:
            flash('No account found with that email')
            return redirect(url_for('auth.login'))
        
        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password.')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('videos.index'))
    
    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
        