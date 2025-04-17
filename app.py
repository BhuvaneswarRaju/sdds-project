from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from cryptography.fernet import Fernet
import os
import time
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'sdds-secret-key'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# Generate or load key
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

# === ROUTES ===

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    uploaded_file = request.files.get('file')
    email = request.form.get('email')

    if uploaded_file and uploaded_file.filename != '':
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encrypted_path = file_path + '.enc'

        file_data = uploaded_file.read()
        encrypted_data = fernet.encrypt(file_data)

        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)

        download_link = url_for('download_file', filename=filename + '.enc', _external=True)

        # Optional email notification
        if email and email.strip() != '':
            try:
                send_email_notification(email, download_link)
            except Exception as e:
                print(f"Email failed: {e}")

        return render_template('success.html', link=download_link)

    flash('No file selected.')
    return redirect(url_for('home'))

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    uploaded_file = request.files.get('file')
    if uploaded_file and uploaded_file.filename.endswith('.enc'):
        filename = secure_filename(uploaded_file.filename)
        encrypted_data = uploaded_file.read()
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
        except Exception:
            return "Decryption failed. Invalid or corrupted file.", 400

        decrypted_filename = filename.rsplit('.enc', 1)[0]
        decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)

        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)

        return send_from_directory(app.config['UPLOAD_FOLDER'], decrypted_filename, as_attachment=True)

    flash('Invalid encrypted file.')
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return "<h3>❌ This file is no longer available.</h3><a href='/'>← Go back</a>", 404

    os.remove(file_path)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# === ERROR HANDLER ===

@app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return "<h3>⚠️ File too large. Maximum allowed size is 5MB.</h3><a href='/'>← Go back</a>", 413

# === OPTIONAL EMAIL NOTIFICATION ===

def send_email_notification(recipient_email, download_link):
    sender_email = "sdds.notify@gmail.com"
    app_password = "your_app_password_here"  # Use App Password from Gmail settings

    subject = "🔐 Your Encrypted File is Ready"
    body = f"""
    Hello,

    Your encrypted file is ready to be downloaded from the secure link below:

    {download_link}

    ⚠️ This file will self-destruct after one access.

    Regards,
    SDDS
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "SDDS Notify <sdds.notify@gmail.com>"
    msg['To'] = recipient_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

# === START SERVER ===

if __name__ == '__main__':
    app.run(debug=True)
