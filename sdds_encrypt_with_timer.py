from cryptography.fernet import Fernet
from datetime import datetime
import json, os, sys

def generate_key():
    key = Fernet.generate_key()
    with open("sdds.key", "wb") as f:
        f.write(key)

def load_key():
    return open("sdds.key", "rb").read()

def encrypt_file(filename, expire_in_sec):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    encrypted_filename = filename + ".enc"
    with open(encrypted_filename, "wb") as enc_file:
        enc_file.write(encrypted)

    metadata = {
        "filename": encrypted_filename,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expire_in": expire_in_sec
    }

    with open(encrypted_filename + ".meta", "w") as meta_file:
        json.dump(metadata, meta_file)

    print(f"✅ Encrypted and will self-destruct in {expire_in_sec} seconds.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python sdds_encrypt_with_timer.py <filename> <expire_in_sec>")
        sys.exit(1)

    generate_key()
    encrypt_file(sys.argv[1], int(sys.argv[2]))
