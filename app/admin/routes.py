from flask import jsonify, render_template, redirect, url_for, abort, request
from flask_login import current_user, login_required
from app.models import TutorProfile, User
from ..extensions import db
from . import admin

#You can still add flash messages to these when you are designing it

@admin.route('/application')
@login_required
def index():
    if not current_user.is_admin:
        abort(403)
    else:
        applications = TutorProfile.query.filter_by(is_approved=False).all()

    return jsonify({'applications':[{
                                    'tutor_id': a.id,
                                    'tutor_name': a.user.full_name, 
                                    'bio':a.bio,
                                    'courses': a.courses} for a in applications]}),200
      


@admin.route('/approve/<int:tutor_id>', methods=['POST'])
@login_required
def approve(tutor_id):
    if not current_user.is_admin:
      abort(403)
    else:
      profile = TutorProfile.query.get_or_404(tutor_id)
      profile.user.is_tutor = True
      profile.is_approved = True
      db.session.commit()
      return jsonify({'message':'Tutor profile approved.'}),201


@admin.route('/reject/<int:tutor_id>', methods=['POST'])
@login_required
def reject(tutor_id):
    if not current_user.is_admin:
      abort(403)
    else:
      profile = TutorProfile.query.get_or_404(tutor_id)
      db.session.delete(profile)
      db.session.commit()
      return jsonify({'message':'Tutor profile rejected.'}),201


# Admin should have a cascade delete and know how to handle integrity Errors if a tutor is late dropped