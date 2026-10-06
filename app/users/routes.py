from flask_login import login_required, current_user
from flask import jsonify, render_template, url_for, redirect, request, current_app, flash
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


@users.route('/profile')
@login_required
def profile():
    #Can put edit buttons
    reviews = current_user.reviews
    return jsonify({
        'name': current_user.full_name,
        'university': current_user.university.name,
        'faculty': current_user.faculty,
        'department': current_user.department,
        'level': current_user.level,
        'reviews': [{
              'video_title': r.video.title,
              'comment': r.comment,
              'rating': r.rating,
              'review_id': r.id,
              'video_id': r.video.id,
              'created_at': r.created_at
           } for r in current_user.reviews]



       }), 200

def avatar_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

def remove_avatar_file(filename):
    if not filename:
      return
    path = avatar_path(filename)
    if os.path.exists(path):
      os.remove(path)
    
@users.route('/upload_avatar', methods=["POST"])
@login_required
def upload_avatar():
    avatar_form = AvatarForm()
    file = request.files.get('avatar')
    if avatar_form.validate_on_submit():
      if file:
        old_filename = current_user.avatar_filename
        extension = file.filename.rsplit('.',1)[1].lower()
        filename = uuid.uuid4().hex + '.' + extension
        file.save(avatar_path(filename))
        current_user.avatar_filename = filename
        db.session.commit()
        remove_avatar_file(old_filename)
        return jsonify({'message':'Upload Successful'}), 201
      
    else:
      return jsonify({'error':avatar_form.errors}), 400

#delete profile pic
@users.route('/delete_avatar', methods=['DELETE'])
@login_required
def delete_avatar():
  if not current_user.avatar_filename:
    return jsonify({'error':'No file to delete'}), 400 
  
  
  filename = current_user.avatar_filename 
  print(filename)
  remove_avatar_file(filename)
  current_user.avatar_filename = None
  db.session.commit()
  return jsonify({'message':'Deletion Successful'}), 200   




#A way to delete files after they have been re-uploaded to avoid disc usage