from flask import Flask, render_template, request, send_from_directory, redirect, url_for, make_response
import os
from cryptography.fernet import Fernet

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

# Ensure uploads/ exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load or generate key
KEY_PATH = 'sdds.key'
if not os.path.exists(KEY_PATH):
    key = Fernet.generate_key()
    with open(KEY_PATH, 'wb') as f:
        f.write(key)
else:
    with open(KEY_PATH, 'rb') as f:
        key = f.read()

fernet = Fernet(key)

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Encrypt + upload
@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)

        # Encrypt and save
        file_data = uploaded_file.read()
        encrypted_data = fernet.encrypt(file_data)

        with open(file_path + '.enc', 'wb') as enc_file:
            enc_file.write(encrypted_data)

        # Generate download link
        download_link = url_for('download_file', filename=uploaded_file.filename + '.enc', _external=True)
        return render_template('success.html', link=download_link)

    return redirect(url_for('home'))

# Decrypt uploaded file
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
            return "<h2>❌ Decryption failed. Invalid or corrupt file.</h2><p><a href='/'>← Go back</a></p>"

    return redirect(url_for('home'))

# Show download confirmation page
@app.route('/uploads/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        # Block bots/previews
        user_agent = request.headers.get('User-Agent', '').lower()
        if "whatsapp" in user_agent or "bot" in user_agent or "preview" in user_agent or "fetch" in user_agent:
            return make_response("⏳ Preparing your file. Please open this link in a browser.", 200)

        # Show branded download page
        return render_template("download.html", filename=filename)

    return "<h2>❌ This file is no longer available.</h2><p><a href='/'>← Go back</a></p>", 404

# Actual download action (POST only)
@app.route('/start-download/<filename>', methods=['POST'])
def start_download(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        os.remove(file_path)
        return response

    return "<h2>❌ This file is no longer available or already downloaded.</h2><p><a href='/'>← Go back</a></p>", 404

# File too large error
@app.errorhandler(413)
def file_too_large(e):
    return "<h2>⚠️ File too large!</h2><p>Upload limit: 5MB</p><p><a href='/'>← Go back</a></p>", 413

# Run app (Render-compatible)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
