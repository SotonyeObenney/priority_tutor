from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, current_app, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from ..models import TutorProfile, User
from flask import Blueprint
from ..extensions import db

#for file handling
import uuid
import os
from werkzeug.utils import secure_filename


from . import users

class AvatarForm(FlaskForm):
    avatar = FileField('avatar', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only')])


@users.route('/')
@login_required
def profile():
    print()
    #   <!-- Display name, university, faculty, department, level
    current_user.full_name
    current_user.university.name
    current_user.faculty
    current_user.department
    current_user.level
    print(current_user.full_name)

    reviews = current_user.reviews
  

    return render_template("users/profile.html", current_user=current_user, reviews=reviews)

class MyForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    
@users.route('/upload_avatar', methods=["GET", "POST"])
@login_required
def upload_avatar():
    avatar_form = AvatarForm()
    file = request.files.get('avatar')
    if avatar_form.validate_on_submit():
      if file:
          extension = file.filename.rsplit('.',1)[1].lower()
          filename = uuid.uuid4().hex + '.' + extension
          file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
          current_user.avatar_filename = filename
          print(current_user.avatar_filename)
          db.session.commit()
          flash("Upload Successful")
    return render_template('users/upload.html', form=avatar_form)
    