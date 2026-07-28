from flask import render_template, redirect, url_for, abort, request
from flask_login import current_user, login_required
from app.models import TutorProfile, User
from app import db
from . import admin

#You can still add flash messages to these when you are designing it

@admin.route('/application')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    else:
        applications = TutorProfile.query.filter_by(is_approved=False).all()
        
    return render_template('admin/index.html', applications=applications)

@admin.route('/approve/<int:tutor_id>', methods=['POST'])
@login_required
def approve(tutor_id):
    if not current_user.is_admin:
      abort(403)
    else:
      profile = db.session.get(TutorProfile, tutor_id)
      profile.user.is_tutor = True
      profile.is_approved = True
      db.session.commit()
      return redirect(url_for('admin.index'))

@admin.route('/reject/<int:tutor_id>', methods=['POST'])
@login_required
def reject(tutor_id):
    if not current_user.is_admin:
      abort(403)
    else:
      profile = db.session.get(TutorProfile, tutor_id)
      db.session.delete(profile)
      db.session.commit()
      return redirect(url_for('admin.index'))