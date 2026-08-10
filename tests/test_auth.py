from werkzeug.security import generate_password_hash

def test_register_creates_user(client, db, app):
    # Arrange: register needs a real university to point at
    from app.models import University
    with app.app_context():
        uni = University(name="Test Uni", country="Nigeria")
        db.session.add(uni)
        db.session.commit()
        uni_id = uni.id

    # Act: do the thing we're actually testing
    response = client.post('/auth/register', data={
        'email': 'student@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'full_name': 'Test Student',
        'faculty': 'Computing',
        'department': 'CS',
        'level': 200,
        'university_id': uni_id,
    })

    # Assert: check it actually worked
    assert response.status_code == 302
    from app.models import User
    with app.app_context():
        user = User.query.filter_by(email='student@test.com').first()
        assert user is not None
        assert user.full_name == 'Test Student'



def test_register_duplicate_email(client, db, app):
    from app.models import University
    with app.app_context():
        uni = University(name="Test Uni", country="Nigeria")
        db.session.add(uni)
        db.session.commit()
        uni_id = uni.id

    payload = {
        'email': 'student@test.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'full_name': 'Test Student', 
        'faculty': 'Computing',
        'department': 'CS',
        'level': 200,
        'university_id': uni_id,
    }

    # First registration — should succeed
    first_response = client.post('/auth/register', data=payload)
    assert first_response.status_code == 302
    assert first_response.location == '/auth/login'

    # Second registration, same email — should be rejected
    second_response = client.post('/auth/register', data=payload)
    assert second_response.status_code == 302
    assert second_response.location == '/auth/register'

    with app.app_context():
        from app.models import User
        count = User.query.filter_by(email='student@test.com').count()
        assert count == 1


def test_login_wrong_password(app, client, db):
    with app.app_context():
        from app.models import University
        uni = University(name="Test Uni", country="Nigeria")
        db.session.add(uni)
        db.session.commit()
        uni_id = uni.id
    register_payload = {
          'email': 'student@test.com',
          'password': 'password123',
          'confirm_password': 'password123',
          'full_name': 'Test Student', 
          'faculty': 'Computing',
          'department': 'CS',
          'level': 200,
          'university_id': uni_id,
      }

    login_payload = {
        'email': 'student@test.com',
        'password': 'wrong123',
        }

      # First registration — should succeed
    register = client.post('/auth/register', data=register_payload)
    assert register.status_code == 302
    assert register.location == '/auth/login'

    login_attempt = client.post('/auth/login', data=login_payload)
    assert login_attempt.status_code == 302
    assert login_attempt.location == '/auth/login'


def test_login_success(app, client, db):
    with app.app_context():
        from app.models import University
        uni = University(name="Test Uni", country="Nigeria")
        db.session.add(uni)
        db.session.commit()
        uni_id = uni.id
    register_payload = {
          'email': 'student@test.com',
          'password': 'password123',
          'confirm_password': 'password123',
          'full_name': 'Test Student', 
          'faculty': 'Computing',
          'department': 'CS',
          'level': 200,
          'university_id': uni_id,
      }

    login_payload = {
        'email': 'student@test.com',
        'password': 'password123',
        }

    register = client.post('/auth/register', data=register_payload)
    assert register.status_code == 302
    assert register.location == '/auth/login'

    login_attempt = client.post('/auth/login', data=login_payload)
    assert login_attempt.status_code == 302
    assert login_attempt.location == '/'


def test_upload_video_requires_tutor(app, client, db):
    with app.app_context():
        from app.models import University
        uni = University(name="Test Uni", country="Nigeria")
        db.session.add(uni)
        db.session.commit()
        uni_id = uni.id
    register_payload = {
          'email': 'student@test.com',
          'password': 'password123',
          'confirm_password': 'password123',
          'full_name': 'Test Student', 
          'faculty': 'Computing',
          'department': 'CS',
          'level': 200,
          'university_id': uni_id,
      }

    login_payload = {
        'email': 'student@test.com',
        'password': 'password123',
        }

    video_payload = {
        'title': 'C language',
        'course_code': 'COS 202',
        'description': 'This is a video description',
        'youtube_url': 'https://youtu.be/dTp0c41XnrQ?si=kafnG0FQYGZjYjR1',
        'price': '7000',
        'is_free': 'False',

        }

      # First registration — should succeed
    register = client.post('/auth/register', data=register_payload)
    assert register.status_code == 302
    assert register.location == '/auth/login'

    login_attempt = client.post('/auth/login', data=login_payload)
    assert login_attempt.status_code == 302
    assert login_attempt.location == '/'

    upload_video_attempt = client.post('/videos/upload', data=video_payload)
    assert upload_video_attempt.status_code == 403


def test_show_video_access_gating(app, client, db):
    with app.app_context():
        from app.models import University, TutorProfile, Video, User
        uni = University(name="Test Uni", country="Nigeria")
        db.session.add(uni)
        db.session.flush()
        uni_id = uni.id

        user1 = User(
            email='user_1@email.com',
            password_hash=generate_password_hash("123456"),
            full_name='User 1 Tutor',
            faculty='Computing',
            department='Computer Science',
            level=300,
            university_id=1,
            is_student=True,
            is_tutor=True,
            is_admin=False
        )
        db.session.add(user1)
        db.session.flush()

        new_tutor = TutorProfile(
            user_id=user1.id,
            bio="I like teaching",
            courses="COS 202, PHY 102, MTH 102, BUS 202"
            )
        db.session.add(new_tutor)
        db.session.flush()


        #creating videos for user_1
        user1_video = Video(
              tutor_id = new_tutor.id,
              title = "Test video for tutor profile 11",
              description = "Learn to code",
              youtube_url = "https://youtu.be/dTp0c41XnrQ?si=kafnG0FQYGZjYjR1",
              course_code = "COS 202",
              price = 1000
            )


        db.session.add(user1_video)
        db.session.commit()


        register_payload = {
                  'email': 'student@test.com',
                  'password': 'password123',
                  'confirm_password': 'password123',
                  'full_name': 'Test Student', 
                  'faculty': 'Computing',
                  'department': 'CS',
                  'level': 200,
                  'university_id': 1,
              }

        login_payload = {
                'email': 'student@test.com',
                'password': 'password123',
                }

        user2_register = client.post('/auth/register', data=register_payload)
        assert user2_register.status_code == 302
        assert user2_register.location == '/auth/login'

        user2_login_attempt = client.post('/auth/login', data=login_payload)
        assert user2_login_attempt.status_code == 302
        assert user2_login_attempt.location == '/'

        user2_view_video_attempt = client.get('/videos/show_video/1')
        assert user2_view_video_attempt.status_code == 200
        body = user2_view_video_attempt.get_data(as_text=True)
        assert "You must buy this video to watch it" in body


        #To check if client has bought the video we will try and leave a review
        with app.app_context():
            from app.models import Video, Purchase, User 
            user2 = User.query.filter_by(email='student@test.com').first()
            user1_video = Video.query.get(user1_video.id)
            purchase = Purchase.query.filter_by(student_id=user2.id, video_id=user1_video.id).first()
            assert purchase == None
            

            new_purchase = Purchase(
                student_id = 2,
                video_id = 1,
                amount_paid = 1000,
                paystack_reference = "fake-ref"
                )
            db.session.add(new_purchase)
            db.session.commit()
            purchase = Purchase.query.filter_by(student_id=user2.id, video_id=user1_video.id).first()
            assert not purchase == None

            user2_view_video_attempt = client.get('/videos/show_video/1')
            assert user2_view_video_attempt.status_code == 200
            assert "You must buy this video to watch it" in body
            
                
            

def test_review_requires_purchase(app, client, db):
    with app.app_context():
    #set up the database
            from app.models import University, TutorProfile, Video, User
            uni = University(name="Test Uni", country="Nigeria")
            db.session.add(uni)
            db.session.flush()
            uni_id = uni.id
    
            user1 = User(
                email='user_1@email.com',
                password_hash=generate_password_hash("123456"),
                full_name='User 1 Tutor',
                faculty='Computing',
                department='Computer Science',
                level=300,
                university_id=1,
                is_student=True,
                is_tutor=True,
                is_admin=False
            )
            db.session.add(user1)
            db.session.flush()
    
            new_tutor = TutorProfile(
                user_id=user1.id,
                bio="I like teaching",
                courses="COS 202, PHY 102, MTH 102, BUS 202"
                )
            db.session.add(new_tutor)
            db.session.flush()
    
    
            #creating videos for user_1
            user1_video = Video(
                  tutor_id = new_tutor.id,
                  title = "Test video for tutor profile 11",
                  description = "Learn to code",
                  youtube_url = "https://youtu.be/dTp0c41XnrQ?si=kafnG0FQYGZjYjR1",
                  course_code = "COS 202",
                  price = 1000
                )
    
    
            db.session.add(user1_video)
            db.session.commit()
    
    #login user
            register_payload = {
                      'email': 'student@test.com',
                      'password': 'password123',
                      'confirm_password': 'password123',
                      'full_name': 'Test Student', 
                      'faculty': 'Computing',
                      'department': 'CS',
                      'level': 200,
                      'university_id': 1,
                  }
    
            login_payload = {
                    'email': 'student@test.com',
                    'password': 'password123',
                    }

            user2_register = client.post('/auth/register', data=register_payload)
            assert user2_register.status_code == 302
            
            login_attempt = client.post('/auth/login', data=login_payload)
            assert login_attempt.status_code == 302
            review_payload = {
              "rating" : "5",
              "comment" : "Test review"
                }
            user2_review_attempt = client.post('videos/review/1', data=review_payload, follow_redirects=True)

            assert user2_review_attempt.status_code == 200
            body = user2_review_attempt.get_data(as_text=True)
            assert "Review succesfully added" not in  body

    #make payment
        #To check if client has bought the video we will try and leave a review
            with app.app_context():
                from app.models import Video, Purchase, User 
                user2 = User.query.filter_by(email='student@test.com').first()
                user1_video = Video.query.get(user1_video.id)
                purchase = Purchase.query.filter_by(student_id=user2.id, video_id=user1_video.id).first()
                assert purchase == None
                
                new_purchase = Purchase(
                    student_id = 2,
                    video_id = 1,
                    amount_paid = 1000,
                    paystack_reference = "fake-ref"
                    )
                db.session.add(new_purchase)
                db.session.commit()
                purchase = Purchase.query.filter_by(student_id=user2.id, video_id=user1_video.id).first()

                assert not purchase == None
                user2_review_attempt = client.post('videos/review/1', data=review_payload, follow_redirects=True)
                assert user2_review_attempt.status_code == 200
                body = user2_review_attempt.text
                assert "Review succesfully added" in body

            




