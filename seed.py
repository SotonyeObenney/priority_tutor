
from datetime import datetime as dt
from app.extensions import db
from app.models import User, TutorProfile, Video, University
from werkzeug.security import generate_password_hash
from app import create_app

app = create_app()

with app.app_context():

    new_user = User(
            email='tutor1@email.com',
            password_hash=generate_password_hash("123456"),
            full_name='Tutor 1',
            faculty='Computing',
            department='Computer Science',
            level=300,
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
        courses = "COS 202, PHY 102, MTH 102, BUS 202"
    )
    db.session.add(new_tutor)
    db.session.flush()

    video = Video(
        tutor_id = new_tutor.id,
        title = "Test video for tutor profile 11",
        description = "Learn to code",
        youtube_url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DAJbJYwEduso&ved=2ahUKEwjnmvPeu7iUAxVzQkEAHV06FxgQkPEHegQIGBAB&usg=AOvVaw2g_sI-9V8rGXiAqHByXJCb",
        course_code = "COS 202",
        created_at = dt.now()
        )
     
    video_1 = Video(
        tutor_id = new_tutor.id,
        title = "Test video for tutor profile 11",
        description = "Learn to code",
        youtube_url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DAJbJYwEduso&ved=2ahUKEwjnmvPeu7iUAxVzQkEAHV06FxgQkPEHegQIGBAB&usg=AOvVaw2g_sI-9V8rGXiAqHByXJCb",
        course_code = "COS 202",
        created_at = dt.now()
        )
    
    video_2 = Video(
        tutor_id = new_tutor.id,
        title = "How to make chicken chips",
        description = "Learn to code",
        youtube_url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DAJbJYwEduso&ved=2ahUKEwjnmvPeu7iUAxVzQkEAHV06FxgQkPEHegQIGBAB&usg=AOvVaw2g_sI-9V8rGXiAqHByXJCb",
        course_code = "COS 202",
        created_at = dt.now()
        )
    
    video_3 = Video(
        tutor_id = new_tutor.id,
        title = "video_3",
        description = "Learn to code",
        youtube_url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DAJbJYwEduso&ved=2ahUKEwjnmvPeu7iUAxVzQkEAHV06FxgQkPEHegQIGBAB&usg=AOvVaw2g_sI-9V8rGXiAqHByXJCb",
        course_code = "COS 302",
        created_at = dt.now()
        )

    db.session.add(video)
    db.session.add(video_1)
    db.session.add(video_2)
    db.session.add(video_3)

    db.session.commit()