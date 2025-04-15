from cryptography.fernet import Fernet
import sys

# Generate and save key
def generate_key():
    key = Fernet.generate_key()
    with open("sdds.key", "wb") as key_file:
        key_file.write(key)

# Load key from file
def load_key():
    return open("sdds.key", "rb").read()

# Encrypt a file
def encrypt_file(filename):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    with open(filename + ".enc", "wb") as encrypted_file:
        encrypted_file.write(encrypted)

    print(f"✅ Encrypted {filename} → {filename}.enc")

# Main script
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 encrypt_file.py <filename>")
        sys.exit(1)

    generate_key()
    encrypt_file(sys.argv[1])
