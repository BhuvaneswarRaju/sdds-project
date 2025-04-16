from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import time
import cleanup  # Auto-runs cleanup to delete expired files
from cryptography.fernet import Fernet

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# 🛠 Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔐 Load or generate encryption key
KEY_PATH = 'sdds.key'
if not os.path.exists(KEY_PATH):
    key = Fernet.generate_key()
    with open(KEY_PATH, 'wb') as key_file:
        key_file.write(key)
else:
    with open(KEY_PATH, 'rb') as key_file:
        key = key_file.read()

fernet = Fernet(key)

# 🌐 Homepage
@app.route('/')
def home():
    return render_template('index.html')

# 🔐 Encrypt + Save
@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)

        # Encrypt contents
        file_data = uploaded_file.read()
        encrypted_data = fernet.encrypt(file_data)

        with open(file_path + '.enc', 'wb') as enc_file:
            enc_file.write(encrypted_data)

        # ⏳ Save expiration time
        expire_in = int(request.form.get('expiry', 86400))  # default 1 day
        expires_at = int(time.time()) + expire_in
        meta_path = file_path + '.enc.meta'
        with open(meta_path, 'w') as meta_file:
            meta_file.write(str(expires_at))

        # 🔗 One-time link
        download_link = url_for('download_file', filename=uploaded_file.filename + '.enc', _external=True)
        return render_template('success.html', link=download_link)

    return redirect(url_for('home'))

# 🔓 Decrypt file
@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    uploaded_file = request.files['file']
    if uploaded_file and uploaded_file.filename.endswith('.enc'):
        enc_data = uploaded_file.read()
        try:
            decrypted_data = fernet.decrypt(enc_data)
            original_filename = uploaded_file.filename.replace('.enc', '')
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)

            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return send_from_directory(app.config['UPLOAD_FOLDER'], original_filename, as_attachment=True)
        except:
            return "<h2>❌ Decryption failed.</h2><p>Invalid file or key.</p><p><a href='/'>← Go back</a></p>"

    return redirect(url_for('home'))

# 💣 One-time download + auto-delete
@app.route('/uploads/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    meta_path = file_path + '.meta'

    if os.path.exists(file_path):
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        os.remove(file_path)
        if os.path.exists(meta_path):
            os.remove(meta_path)
        return response
    else:
        return "<h2>❌ This file is no longer available (it was deleted after first download or expired).</h2><p><a href='/'>← Go back</a></p>", 404

# ⚠️ Large file handler
@app.errorhandler(413)
def too_large(e):
    return "<h2>⚠️ File too large!</h2><p>Please upload a file under 5MB.</p><p><a href='/'>← Go back</a></p>", 413

# ▶️ Run on proper port for Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
