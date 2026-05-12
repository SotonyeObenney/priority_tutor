from .extensions import db, login_manager
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


class TutorProfile(db.Model):
    __tablename__ = 'tutor_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    courses = db.Column(db.String(255), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    avg_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)

    videos = db.relationship('Video', backref='tutor', lazy=True)


class Video(db.Model):
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(300), nullable=False)
    course_code = db.Column(db.String(20), nullable=False)
    is_free = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, default=0.0)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False)

    reviews = db.relationship('Review', backref='video', lazy=True)

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('video_id', 'student_id', name='unique_student_video_review'),
        )
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))