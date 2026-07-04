from flask import render_template, redirect, url_for, abort, request
from flask_login import current_user, login_required
from app.models import TutorProfile, User
from app import db
from . import admin

@admin.route('/application')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    else:
        print("Hello World")
        applications = TutorProfile.query.filter_by(is_approved=False).all()
        
    return render_template('admin/index.html', applications=applications)

@admin.route('/approve/<int:tutor_id>', methods=['POST'])
def approve(tutor_id):
    print(tutor_id)
    profile = db.session.get(TutorProfile, tutor_id)
    profile.user.is_tutor = True
    profile.is_approved = True
    db.session.commit()
    print("Approval Done!")
    return redirect(url_for('admin.index'))

@admin.route('/reject/<int:tutor_id>', methods=['POST'])
def reject(tutor_id):
    print(tutor_id)
    profile = db.session.get(TutorProfile, tutor_id)
    db.session.delete(profile)
    db.session.commit()
    print(profile)
    return redirect(url_for('admin.index'))