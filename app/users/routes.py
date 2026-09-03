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
              'video_id': r.id,
              'created_at': r.created_at
           } for r in current_user.reviews]



       }), 200


    
@users.route('/upload_avatar', methods=["POST"])
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

        db.session.commit()
        return jsonify({'message':'Upload Successful'}), 201
      
      else:
        return jsonify({'error':avatar_form.errors}), 400




#A way to delete files after they have been re-uploaded to avoid disc usage