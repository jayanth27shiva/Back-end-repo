from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import subprocess

app = Flask(__name__)
CORS(app)  # Vulnerability: Overly permissive CORS policy

# Vulnerable configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'very-secret-key'  # Vulnerability: Weak secret key
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Vulnerability: Hardcoded credentials

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))  # Vulnerability: Plaintext passwords
    role = db.Column(db.String(20))

@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data['username'] == ADMIN_USERNAME and data['password'] == ADMIN_PASSWORD:
        token = jwt.encode({'role': 'admin', 'exp': datetime.utcnow() + timedelta(days=1)}, app.config['SECRET_KEY'])
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/get-db', methods=['GET'])
def get_db():
    return send_file('learning.db', as_attachment=True)  # Vulnerability: Exposes database

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file provided'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'message': 'File uploaded successfully'})  # Vulnerability: No file type validation

@app.route('/api/debug', methods=['POST'])
def debug():
    command = request.json.get('cmd')
    try:
        output = subprocess.check_output(command, shell=True)  # Vulnerability: Arbitrary command execution
        return jsonify({'output': output.decode()})
    except Exception as e:
        return jsonify({'error': str(e)})  # Vulnerability: Stack trace exposure

@app.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out'})  # Vulnerability: No session invalidation

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=4000)
