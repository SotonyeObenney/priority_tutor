
from datetime import datetime as dt
from app.extensions import db
from app.models import User, TutorProfile, Video, University
from werkzeug.security import generate_password_hash
from app import create_app

app = create_app()

with app.app_context():

    new_user = User(
            email='user@email.com',
            password_hash=generate_password_hash("123456"),
            full_name='David Jolly',
            faculty='Computing',
            department='Computer Science',
            level=200,
            university_id=1,
            is_student=True,
            is_tutor=True,
            is_admin=False
        )
    db.session.add(new_user)
    db.session.flush()

    new_tutor = TutorProfile(
        user_id = new_user.id,
        bio = "I like teaching",
        courses = "COS 202"
    )
    db.session.add(new_tutor)
    db.session.flush()

    video = Video(
        tutor_id = new_tutor.id,
        title = "Java Programming",
        description = "Learn to code",
        youtube_url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3D4Ef9pdaVTzA&ved=2ahUKEwjFlOnx47eUAxXFUUEAHa_TBFEQkPEHegQIHhAB&usg=AOvVaw2MLZTyt_CBsrrYSkmvLX5Y",
        course_code = "COS 202",
        created_at = dt.now()
        )
    db.session.add(video)
    db.session.commit()