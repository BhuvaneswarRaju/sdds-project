from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from cryptography.fernet import Fernet

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🛡️ Limit max file size to 5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# ✅ Always create uploads folder (even on Render)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔑 Load or generate encryption key
KEY_PATH = 'sdds.key'
if not os.path.exists(KEY_PATH):
    key = Fernet.generate_key()
    with open(KEY_PATH, 'wb') as key_file:
        key_file.write(key)
else:
    with open(KEY_PATH, 'rb') as key_file:
        key = key_file.read()

fernet = Fernet(key)

# 🌐 Home Page
@app.route('/')
def home():
    return render_template('index.html')

# 🔐 Encrypt route
@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)

        file_data = uploaded_file.read()
        encrypted_data = fernet.encrypt(file_data)

        with open(file_path + '.enc', 'wb') as enc_file:
            enc_file.write(encrypted_data)

        download_link = url_for('download_file', filename=uploaded_file.filename + '.enc', _external=True)
        return f"<h2>✅ File Encrypted!</h2><p><a href='{download_link}'>Download Encrypted File</a></p><p><a href='/'>← Go back</a></p>"

    return redirect(url_for('home'))

# 🔓 Decrypt route
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

# �� Download link
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ▶ Run locally
if __name__ == '__main__':
    app.run(debug=True)
