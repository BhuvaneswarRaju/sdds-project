from cryptography.fernet import Fernet
import sys, os

def load_key():
    return open("sdds.key", "rb").read()

def decrypt_and_delete(filename):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = fernet.decrypt(encrypted)

    output_file = "decrypted_" + filename.replace(".enc", "")
    with open(output_file, "wb") as f:
        f.write(decrypted)

    os.remove(filename)
    print(f"✅ Decrypted to {output_file} and deleted {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python decrypt_file_once.py <encrypted_filename>")
        sys.exit(1)

    decrypt_and_delete(sys.argv[1])
