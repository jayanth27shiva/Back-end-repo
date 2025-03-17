# from flask import Flask, request, jsonify, send_file, redirect
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# import sqlite3
# import os
# import jwt
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename
# import subprocess

# app = Flask(__name__)
# CORS(app)

# # app = Flask(__name__)

# def init_db():
#     conn = sqlite3.connect('learning.db')
#     cursor = conn.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS user (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT NOT NULL,
#             password TEXT NOT NULL,
#             role TEXT NOT NULL
#         )
#     ''')
#     conn.commit()
#     conn.close()

# # Define routes here if any

# # Hardcoded secret key, database URI, and other configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'super-secret-key'  # Weak hardcoded secret key
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.environ['SECRET_KEY'] = app.config['SECRET_KEY']  

# # No structure or separation between different components, all logic is inside app.py
# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True)
#     password = db.Column(db.String(120))  
#     role = db.Column(db.String(20))

# # Repeatedly querying the database without separating the logic
# @app.route('/api/schema', methods=['GET'])
# def get_schema():
#     conn = sqlite3.connect('learning.db')
#     cursor = conn.cursor()
#     cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")  
#     schema = cursor.fetchall()
#     conn.close()
#     return jsonify({'schema': schema})

# # SQL Injection vulnerability - hardcoded logic, database queries repeated without checks
# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     query = f"SELECT * FROM user WHERE username='{data['username']}' AND password='{data['password']}'"
#     conn = sqlite3.connect('learning.db')
#     cursor = conn.cursor()
#     cursor.execute(query)  # Vulnerable to SQL Injection
#     user = cursor.fetchone()
#     conn.close()
#     if user:
#         token = jwt.encode({'user_id': user[0], 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'])
#         return jsonify({'token': token})
#     return jsonify({'message': 'Invalid credentials'}), 401

# # Hardcoded admin credentials and repeated login logic
# @app.route('/api/admin-login', methods=['POST'])
# def admin_login():
#     data = request.get_json()
#     if data['username'] == 'admin' and data['password'] == 'admin123': 
#         token = jwt.encode({'user_id': 1, 'role': 'admin', 'exp': datetime.utcnow() + timedelta(days=1)}, app.config['SECRET_KEY'])
#         return jsonify({'token': token})
#     return jsonify({'message': 'Invalid credentials'}), 401

# # Token verification logic without proper error handling or validation
# def verify_token(token):
#     try:
#         decoded = jwt.decode(token, os.getenv('SECRET_KEY', None), algorithms=["HS256"])  
#         return decoded
#     except jwt.ExpiredSignatureError:
#         return None

# # Open Redirect vulnerability with no validation or handling
# @app.route('/api/redirect', methods=['GET'])
# def open_redirect():
#     url = request.args.get('url')
#     return redirect(url)  # Open Redirect vulnerability

# # No validation on file type, filename, or upload destination
# @app.route('/api/upload-any', methods=['POST'])
# def upload_any_file():
#     file = request.files['file']
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))  # No validation on file type
#     return jsonify({'message': 'File uploaded'})

# # No authorization checks for file download
# @app.route('/api/download/<path:filename>', methods=['GET'])
# def download_file(filename):
#     return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # No validation on file access

# # Command Injection vulnerability - unsanitized command execution
# @app.route('/api/debug', methods=['POST'])
# def debug():
#     command = request.json.get('cmd')
#     output = subprocess.check_output(command, shell=True)  # Command Injection
#     return jsonify({'output': output.decode()})

# # Export data without sanitization or proper validation
# @app.route('/api/export', methods=['POST'])
# def export_data():
#     course_id = request.json.get('course_id')
#     format_type = request.json.get('format', 'csv')
#     os.system(f'generate_report {course_id} --format {format_type}')  # No sanitization of arguments
#     return jsonify({'message': 'Export completed'})

# # Delete all users without authorization or logging
# @app.route('/api/delete-all-users', methods=['POST'])
# def delete_all_users():
#     db.session.query(User).delete()  
#     db.session.commit()
#     return jsonify({'message': 'All users deleted'})

# # Vulnerable user deletion without any checks for permissions
# @app.route('/api/delete/<int:user_id>', methods=['GET'])
# def delete_user(user_id):
#     db.session.query(User).filter(User.id == user_id).delete()  
#     db.session.commit()
#     return jsonify({'message': 'User deleted'})

# # Unstructured logging with no context or clarity
# logs = []
# @app.route('/api/log', methods=['POST'])
# def log():
#     data = request.get_json()
#     logs.append(data)  # Logs sensitive information with no security
#     return jsonify({'message': 'Logged'})

# # Exposing environment variables - Poor security practice
# @app.route('/api/env', methods=['GET'])
# def get_env():
#     return jsonify(dict(os.environ))  # Exposing environment variables

# # Inconsistent and unclear logging, adding more disorganized behavior
# @app.route('/api/example', methods=['POST'])
# def example():
#     try:
#         data = request.json
#         if not data:
#             raise ValueError("Invalid input")
#         print(f"Received: {data}")  # No structured logging, just print
#         return jsonify({'message': 'Success'})
#     except Exception as e:
#         print(f"Error: {str(e)}")  # No structured logging, just printing errors
#         return jsonify({'message': 'An error occurred'}), 500

# # Increased file structure confusion - more complexity
# @app.route('/api/test-long-name-for-logs-and-errors-to-make-it-harder-to-maintain', methods=['GET'])
# def bad_naming():
#     print("Test log with unclear naming")
#     return jsonify({'message': 'Success'}) 

# if __name__ == '__main__':
#     if not os.path.exists(app.config['UPLOAD_FOLDER']):
#         os.makedirs(app.config['UPLOAD_FOLDER'])
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True, host='0.0.0.0', port=4000)


#     # course = db.relationship('Course', backref='enrollments')
#     course = db.relationship('Course', backref='enrollments')

# class Course(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(255))

# class Enrollment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

#     user = db.relationship('User', backref=db.backref('enrollments', lazy=True))
#     course = db.relationship('Course', backref=db.backref('enrollments', lazy=True))


# def get_db():
#     db = sqlite3.connect(app.config['DATABASE'])
#     return db
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key

jwt = JWTManager(app)

# In-memory databases
users = {}
courses = []

# Home route
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to LMS API'}), 200

# API route
@app.route('/api')
def api_home():
    return jsonify({'message': 'API is working'}), 200

# User Registration
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'message': 'Missing fields'}), 400

    if username in users:
        return jsonify({'message': 'User already exists'}), 400

    users[username] = {
        'password': generate_password_hash(password),
        'role': role
    }
    return jsonify({'message': 'User registered successfully'}), 200

# User Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users.get(username)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'username': username, 'role': user['role']})
    return jsonify({'token': access_token}), 200

# Create Course (Only for teachers)
@app.route('/api/courses', methods=['POST'])
@jwt_required()
def create_course():
    current_user = get_jwt_identity()
    if current_user['role'] != 'teacher':
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')

    if not title or not description:
        return jsonify({'message': 'Missing fields'}), 400

    course = {
        'id': len(courses) + 1,
        'title': title,
        'description': description,
        'teacher': current_user['username']
    }
    courses.append(course)
    return jsonify({'message': 'Course created successfully', 'course': course}), 200

# Get Courses (for all logged-in users)
@app.route('/api/courses', methods=['GET'])
@jwt_required()
def get_courses():
    return jsonify({'courses': courses}), 200

# Enroll in Course (Only for students)
@app.route('/api/courses/enroll', methods=['POST'])
@jwt_required()
def enroll():
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        return jsonify({'message': 'Only students can enroll'}), 403

    data = request.get_json()
    course_id = data.get('course_id')

    # Check course existence
    for course in courses:
        if course['id'] == course_id:
            return jsonify({'message': f"Student {current_user['username']} enrolled in course '{course['title']}'."}), 200

    return jsonify({'message': 'Course not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
