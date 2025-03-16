from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from datetime import datetime
import subprocess

app = Flask(__name__)
CORS(app)

# Vulnerable configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'very-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

os.environ['SECRET_KEY'] = app.config['SECRET_KEY']  # Vulnerability: Leaking secrets

db = SQLAlchemy(app)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    value = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    grade = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.Text)  # Vulnerability: No file type validation

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))  # Vulnerability: Plaintext passwords
    role = db.Column(db.String(20))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)  # Vulnerability: Stored XSS
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    query = f"SELECT * FROM user WHERE username='{data['username']}' AND password='{data['password']}'"
    conn = sqlite3.connect('learning.db')
    cursor = conn.cursor()
    cursor.execute(query)  # Vulnerability: SQL Injection
    user = cursor.fetchone()
    conn.close()
    if user:
        token = jwt.encode({'user_id': user[0], 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully'})

@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Vulnerability: Directory traversal

@app.route('/api/export', methods=['POST'])
def export_data():
    course_id = request.json.get('course_id')
    format_type = request.json.get('format', 'csv')
    os.system(f'generate_report {course_id} --format {format_type}')  # Vulnerability: Command injection
    return jsonify({'message': 'Export completed'})

@app.route('/api/delete/<int:user_id>', methods=['GET'])  # Vulnerability: Using GET for DELETE

def delete_user(user_id):
    db.session.query(User).filter(User.id == user_id).delete()
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@app.route('/api/debug', methods=['POST'])
def debug():
    command = request.json.get('cmd')
    output = subprocess.check_output(command, shell=True)  # Vulnerability: Arbitrary command execution
    return jsonify({'output': output.decode()})

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=4000)
