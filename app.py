from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import os
import smtplib
from email.mime.text import MIMEText
import requests

app = Flask(__name__)
app.secret_key = 'sdds-secret-key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# Load or create encryption key
KEY_FILE = 'sdds.key'
if not os.path.exists(KEY_FILE):
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as f:
        f.write(key)
else:
    with open(KEY_FILE, 'rb') as f:
        key = f.read()

fernet = Fernet(key)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    uploaded_file = request.files.get('file')
    email = request.form.get('email')
    country = request.form.get('country', 'any')

    if uploaded_file and uploaded_file.filename:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        enc_path = file_path + '.enc'

        file_data = uploaded_file.read()
        encrypted_data = fernet.encrypt(file_data)

        with open(enc_path, 'wb') as f:
            f.write(encrypted_data)

        if email:
            with open(enc_path + '.email', 'w') as f:
                f.write(email.strip())

        if country != 'any':
            with open(enc_path + '.geo', 'w') as f:
                f.write(country)

        link = url_for('download_file', filename=filename + '.enc', _external=True)
        return render_template('success.html', link=link)
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def download_file(filename):
    enc_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(enc_path):
        return "<h3>❌ File not found or already deleted.</h3>", 404

    # GEO FENCING VALIDATION
    geo_file = enc_path + '.geo'
    if os.path.exists(geo_file):
        with open(geo_file, 'r') as f:
            allowed_country = f.read().strip()

        try:
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            geo_data = requests.get(f'https://ipapi.co/{ip}/country/').text.strip()
            if geo_data != allowed_country:
                return f"<h3>🚫 Access denied. This file can only be downloaded from {allowed_country}.</h3>", 403
        except Exception as e:
            return f"<h3>🌐 Geo verification failed. Try again later.</h3>", 500

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
