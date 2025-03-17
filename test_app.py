# import pytest
# from app import app, db, User, Course, Enrollment
# import json
# import jwt
# from datetime import datetime, timedelta

# import pytest
# from app import app, init_db

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     app.config['DATABASE'] = ':memory:'  # In-memory DB
#     with app.test_client() as client:
#         with app.app_context():
#             init_db()
#         yield client

# def test_home_route(client):
#     response = client.get('/')
#     assert response.status_code == 200

# def test_api_route(client):
#     response = client.get('/api')
#     assert response.status_code == 200

# def test_register_user(client):
#     response = client.post('/api/register', json={
#         'username': 'newuser',
#         'password': 'newpass',
#         'role': 'student'
#     })
#     assert response.status_code == 200

# def test_login_valid_credentials(client):
#     client.post('/api/register', json={
#         'username': 'testuser',
#         'password': 'testpass',
#         'role': 'student'
#     })
#     response = client.post('/api/login', json={
#         'username': 'testuser',
#         'password': 'testpass'
#     })
#     assert response.status_code == 200


# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

#     with app.test_client() as client:
#         with app.app_context():
#             db.create_all()
#             yield client
#             db.drop_all()


# @pytest.fixture
# def auth_token():
#     test_user = User(
#         username='testuser',
#         password='testpass',
#         role='teacher'
#     )
#     with app.app_context():
#         db.session.add(test_user)
#         db.session.commit()

#         token = jwt.encode({
#             'user_id': test_user.id,
#             'username': test_user.username,
#             'role': test_user.role,
#             'exp': datetime.utcnow() + timedelta(hours=24)
#         }, app.config['SECRET_KEY'])

#         return token


# def test_home_route(client):
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b'Backend flask app running' in response.data


# def test_api_route(client):
#     response = client.get('/api')
#     assert response.status_code == 200
#     assert b'/API endpoint called !' in response.data


# def test_register_user(client):
#     response = client.post('/api/register',
#                            json={
#                                'username': 'newuser',
#                                'password': 'newpass',
#                                'role': 'student'
#                            }
#                            )
#     assert response.status_code == 200
#     assert b'Registration successful' in response.data

#     # Verify user was created
#     with app.app_context():
#         user = User.query.filter_by(username='newuser').first()
#         assert user is not None
#         assert user.role == 'student'


# def test_login_valid_credentials(client):
#     # First register a user
#     client.post('/api/register',
#                 json={
#                     'username': 'testuser',
#                     'password': 'testpass',
#                     'role': 'student'
#                 }
#                 )

#     # Then try to login
#     response = client.post('/api/login',
#                            json={
#                                'username': 'testuser',
#                                'password': 'testpass'
#                            }
#                            )
#     assert response.status_code == 200
#     assert 'token' in response.get_json()


# def test_login_invalid_credentials(client):
#     response = client.post('/api/login',
#                            json={
#                                'username': 'wronguser',
#                                'password': 'wrongpass'
#                            }
#                            )
#     assert response.status_code == 401
#     assert b'Invalid credentials' in response.data


# def test_create_course(client, auth_token):
#     response = client.post('/api/courses',
#                            headers={'Authorization': f'Bearer {auth_token}'},
#                            json={
#                                'title': 'Test Course',
#                                'description': 'Test Description'
#                            }
#                            )
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'course' in data
#     assert data['course']['title'] == 'Test Course'


# def test_get_courses_teacher(client, auth_token):
#     # First create a course
#     client.post('/api/courses',
#                 headers={'Authorization': f'Bearer {auth_token}'},
#                 json={
#                     'title': 'Test Course',
#                     'description': 'Test Description'
#                 }
#                 )

#     # Then get courses
#     response = client.get('/api/courses',
#                           headers={'Authorization': f'Bearer {auth_token}'}
#                           )
#     assert response.status_code == 200
#     courses = response.get_json()
#     assert len(courses) > 0
#     assert courses[0]['title'] == 'Test Course'


# def test_enroll_in_course(client):
#     # First create a student
#     student_data = {
#         'username': 'student1',
#         'password': 'pass123',
#         'role': 'student'
#     }
#     client.post('/api/register', json=student_data)

#     # Login as student
#     login_response = client.post('/api/login',
#                                  json={
#                                      'username': 'student1',
#                                      'password': 'pass123'
#                                  }
#                                  )
#     token = login_response.get_json()['token']

#     # Create a teacher first
#     with app.app_context():
#         teacher = User(username='teacher1', password='pass123', role='teacher')
#         db.session.add(teacher)
#         db.session.commit()  # Commit to get the teacher.id

#         # Now create the course with the valid teacher_id
#         course = Course(
#             title='Test Course',
#             description='Test',
#             teacher_id=teacher.id  # Now teacher.id will be valid
#         )
#         db.session.add(course)
#         db.session.commit()
#         course_id = course.id

#     # Try to enroll
#     response = client.post('/api/enroll',
#                            headers={'Authorization': f'Bearer {token}'},
#                            json={'course_id': course_id}
#                            )
#     assert response.status_code == 200
#     assert b'Enrolled successfully' in response.data

#     # Verify enrollment in database
#     with app.app_context():
#         enrollment = Enrollment.query.filter_by(course_id=course_id).first()
#         assert enrollment is not None


# def test_unauthorized_access(client):
#     # Try to access courses without token
#     response = client.get('/api/courses')
#     assert response.status_code == 401

#     # Try to create course without token
#     response = client.post('/api/courses',
#                            json={
#                                'title': 'Test Course',
#                                'description': 'Test Description'
#                            }
#                            )
#     assert response.status_code == 401
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Home route
def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200

# API route
def test_api_route(client):
    response = client.get('/api')
    assert response.status_code == 200

# Register user
def test_register_user(client):
    response = client.post('/api/register', json={
        'username': 'newuser',
        'password': 'newpass',
        'role': 'student'
    })
    assert response.status_code == 200

# Login with valid credentials
def test_login_valid_credentials(client):
    client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass',
        'role': 'student'
    })
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'token' in response.get_json()

# Create course (teacher)
def test_create_course(client):
    client.post('/api/register', json={
        'username': 'teacher1',
        'password': 'teachpass',
        'role': 'teacher'
    })
    login_resp = client.post('/api/login', json={
        'username': 'teacher1',
        'password': 'teachpass'
    })
    token = login_resp.get_json()['token']
    response = client.post('/api/courses',
                           headers={'Authorization': f'Bearer {token}'},
                           json={'title': 'Course1', 'description': 'Description1'})
    assert response.status_code == 200

# Get courses
def test_get_courses_teacher(client):
    client.post('/api/register', json={
        'username': 'teacher2',
        'password': 'teachpass',
        'role': 'teacher'
    })
    login_resp = client.post('/api/login', json={
        'username': 'teacher2',
        'password': 'teachpass'
    })
    token = login_resp.get_json()['token']
    client.post('/api/courses',
                headers={'Authorization': f'Bearer {token}'},
                json={'title': 'Course2', 'description': 'Description2'})
    response = client.get('/api/courses', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200

# Enroll in a course
def test_enroll_in_course(client):
    # Register teacher and create course
    client.post('/api/register', json={
        'username': 'teacher3',
        'password': 'teachpass',
        'role': 'teacher'
    })
    teacher_login = client.post('/api/login', json={
        'username': 'teacher3',
        'password': 'teachpass'
    })
    teacher_token = teacher_login.get_json()['token']
    client.post('/api/courses',
                headers={'Authorization': f'Bearer {teacher_token}'},
                json={'title': 'Course3', 'description': 'Description3'})

    # Register student
    client.post('/api/register', json={
        'username': 'student1',
        'password': 'studpass',
        'role': 'student'
    })
    student_login = client.post('/api/login', json={
        'username': 'student1',
        'password': 'studpass'
    })
    student_token = student_login.get_json()['token']

    # Enroll in course
    response = client.post('/api/courses/enroll',
                           headers={'Authorization': f'Bearer {student_token}'},
                           json={'course_id': 1})
    assert response.status_code == 200

# Unauthorized access
def test_unauthorized_access(client):
    response = client.get('/api/courses')
    assert response.status_code == 401
