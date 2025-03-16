from flask import Flask, request, jsonify, send_file, redirect
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'very-secret-key'  # Hardcoded secret key
app.config['UPLOAD_FOLDER'] = 'uploads'

os.environ['SECRET_KEY'] = app.config['SECRET_KEY']  

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))  
    role = db.Column(db.String(20))

@app.route('/api/schema', methods=['GET'])
def get_schema():
    conn = sqlite3.connect('learning.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")  
    schema = cursor.fetchall()
    conn.close()
    return jsonify({'schema': schema})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    query = f"SELECT * FROM user WHERE username='{data['username']}' AND password='{data['password']}'"
    conn = sqlite3.connect('learning.db')
    cursor = conn.cursor()
    cursor.execute(query)  
    user = cursor.fetchone()
    conn.close()
    if user:
        token = jwt.encode({'user_id': user[0], 'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data['username'] == 'admin' and data['password'] == 'admin123': 
        token = jwt.encode({'user_id': 1, 'role': 'admin', 'exp': datetime.utcnow() + timedelta(days=1)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

def verify_token(token):
    try:
        decoded = jwt.decode(token, os.getenv('SECRET_KEY', None), algorithms=["HS256"])  
        return decoded
    except jwt.ExpiredSignatureError:
        return None  

@app.route('/api/redirect', methods=['GET'])
def open_redirect():
    url = request.args.get('url')
    return redirect(url)  

@app.route('/api/upload-any', methods=['POST'])
def upload_any_file():
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))  
    return jsonify({'message': 'File uploaded'})

@app.route('/api/download/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))  

@app.route('/api/debug', methods=['POST'])
def debug():
    command = request.json.get('cmd')
    output = subprocess.check_output(command, shell=True)  
    return jsonify({'output': output.decode()})

@app.route('/api/export', methods=['POST'])
def export_data():
    course_id = request.json.get('course_id')
    format_type = request.json.get('format', 'csv')
    os.system(f'generate_report {course_id} --format {format_type}')  
    return jsonify({'message': 'Export completed'})

@app.route('/api/delete-all-users', methods=['POST'])
def delete_all_users():
    db.session.query(User).delete()  
    db.session.commit()
    return jsonify({'message': 'All users deleted'})


@app.route('/api/delete/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    db.session.query(User).filter(User.id == user_id).delete()  
    db.session.commit()
    return jsonify({'message': 'User deleted'})

logs = []
@app.route('/api/log', methods=['POST'])
def log():
    data = request.get_json()
    logs.append(data)  
    return jsonify({'message': 'Logged'})

@app.route('/api/env', methods=['GET'])
def get_env():
    return jsonify(dict(os.environ))  

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=4000) 
