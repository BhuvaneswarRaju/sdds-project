from flask import Flask, render_template, request, send_from_directory, redirect, url_for, make_response
import os
from cryptography.fernet import Fernet
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size

# Make sure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load or generate encryption key
KEY_PATH = 'sdds.key'
if not os.path.exists(KEY_PATH):
    key = Fernet.generate_key()
    with open(KEY_PATH, 'wb') as f:
        f.write(key)
else:
    with open(KEY_PATH, 'rb') as f:
        key = f.read()

fernet = Fernet(key)

# ✅ Email sending function (no password prompt — use app password instead)
def send_notification_email(to_email, filename):
    try:
        sender_email = "sdds.notify@gmail.com"     # 🔁 Replace with your Gmail
        sender_password = "vpvmrurmnpdlphyf"    # 🔁 Replace with your Gmail App Password

        subject = "Your file has been accessed and deleted"
        body = f"Hello,\n\nYour file '{filename}' was downloaded and has been securely deleted from the SDDS server.\n\n- SDDS"
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"✅ Notification email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# === Routes ===

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    uploaded_file = request.files['file']
    user_email = request.form.get('email')

    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        enc_path = file_path + '.enc'

        # Encrypt and save file
        file_data = uploaded_file.read()
        encrypted_data = fernet.encrypt(file_data)

        with open(enc_path, 'wb') as f:
            f.write(encrypted_data)

        # Save optional email (next to the file)
        if user_email:
            with open(enc_path + '.email', 'w') as f:
                f.write(user_email.strip())

        # Generate link
        download_link = url_for('download_file', filename=uploaded_file.filename + '.enc', _external=True)
        return render_template('success.html', link=download_link)

    return redirect(url_for('home'))

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    uploaded_file = request.files['file']
    if uploaded_file and uploaded_file.filename.endswith('.enc'):
        try:
            encrypted_data = uploaded_file.read()
            decrypted_data = fernet.decrypt(encrypted_data)

            original_filename = uploaded_file.filename.replace('.enc', '')
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)

            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return send_from_directory(app.config['UPLOAD_FOLDER'], original_filename, as_attachment=True)
        except:
            return "<h2>❌ Decryption failed.</h2><p><a href='/'>← Go back</a></p>"

    return redirect(url_for('home'))

@app.route('/uploads/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        # Check for bots/previews (like WhatsApp)
        user_agent = request.headers.get('User-Agent', '').lower()
        if "whatsapp" in user_agent or "bot" in user_agent:
            return make_response("⚠️ This link must be opened in a browser.", 200)

        # If email exists, notify
        email_path = file_path + '.email'
        if os.path.exists(email_path):
            with open(email_path, 'r') as f:
                user_email = f.read().strip()
                send_notification_email(user_email, filename.replace('.enc', ''))
            os.remove(email_path)

        return render_template('download.html', filename=filename,
                               display_name=filename.replace('.enc', ''),
                               size=os.path.getsize(file_path))

    return "<h2>❌ This file is no longer available.</h2>", 404

@app.route('/start-download/<filename>', methods=['POST'])
def start_download(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        os.remove(file_path)
        return response
    return "<h2>❌ File already accessed or expired.</h2>", 404

@app.errorhandler(413)
def file_too_large(e):
    return "<h2>⚠️ File too large!</h2><p>Limit: 5MB</p>", 413

if __name__ == '__main__':
    app.run(debug=True)
