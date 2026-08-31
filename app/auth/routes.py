from flask import render_template, redirect, url_for, flash, request, jsonify
from . import auth 
from ..extensions import db
from ..models import User, University
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired #You can also add some length of characters

from flask_login import login_user
from flask_login import logout_user, current_user


# WTF-Forms

class LoginForm(FlaskForm):
  email = EmailField('email', validators=[DataRequired()])
  password = PasswordField('password')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password')
    faculty = StringField('Faculty', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])

    

@auth.route('/register', methods=['POST'])
def register():

    # if current_user.is_authenticated: Have react check this instead and do conditional routing
    #     return redirect(url_for('videos.index'))
    
    register_form = RegisterForm()

    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    full_name = request.form.get('full_name')
    faculty = request.form.get('faculty')
    department = request.form.get('department')
    level = request.form.get('level')
    university_id = request.form.get('university_id')

    

    if not email or not password or not full_name:
      return jsonify({'error':'All fields are required.'}), 400


    if password != confirm_password:
        return jsonify({'error':'Passwords must match'}), 400

    

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email has already been registered'}), 409

    if register_form.validate_on_submit():

      try:
          university_id = int(university_id)
          level = int(level)
      except (TypeError, ValueError):
        return jsonify({'error': 'Level and university must be valid selections.'}), 409

      new_user = User(
          email=email,
          password_hash=generate_password_hash(password),
          full_name=full_name,
          faculty=faculty,
          department=department,
          level=level,
          university_id=university_id,
          is_student=True,
          is_tutor=False,
          is_admin=False
      )

      db.session.add(new_user)
      db.session.commit()
      return jsonify({
          "message": "Registration successful.",
          "user": {"id": new_user.id, "email": new_user.email, "full_name": new_user.full_name}
      }), 201
    # universities = University.query.all() how will react get the university ids?
    # return render_template('auth/register.html', universities=universities, form=register_form)


    

@auth.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("videos.index"))


    login_form = LoginForm()

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    
    
    if not user:
        return jsonify({"error": "No account found with that email."}), 401
    
    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Incorrect password. Please try again."}), 401

    if login_form.validate_on_submit():
      login_user(user)
      return jsonify({
          "message": "Login successful.",
          "user": {"id": user.id, "email": user.email, "full_name": user.full_name, "is_tutor": user.is_tutor}
      }), 200    

#go over how to write restful message dicts
@auth.route('/logout')
def logout():
    logout_user()
    return jsonify({"message": "Logged out."}), 200        