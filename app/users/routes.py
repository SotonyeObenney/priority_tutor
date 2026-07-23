from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request, current_app, flash
from ..models import TutorProfile, User
from flask import Blueprint
from ..extensions import db

#for file handling
import uuid
import os
from werkzeug.utils import secure_filename


from . import users


@users.route('/')
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
    
@users.route('/upload_avatar', methods=["GET", "POST"])
def upload_avatar():
    file = request.files.get('avatar')
    print(f"this is the file name {file}")
    print(f"method{request.method}")
    print(f"files {request.files}")
    print(f"form{request.form}")
    if file:
        extension = file.filename.rsplit('.',1)[1].lower()
        filename = uuid.uuid4().hex + '.' + extension
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        current_user.avatar_filename = filename
        print(current_user.avatar_filename)
        db.session.commit()
        flash("Upload Successful")
    return render_template('users/upload.html')
    