from .extensions import db
from flask_login import UserMixin

class University(db.Model):
    __tablename__ = 'universities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    users = db.relationship('User', backref='university', lazy=True)



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)

    is_student = db.Column(db.Boolean, default=True)
    is_tutor = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    tutor_profile = db.relationship('TutorProfile', backref='user', uselist=False)
    reviews = db.relationship('Review', backref='student', lazy=True)