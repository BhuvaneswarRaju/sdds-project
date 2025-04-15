from cryptography.fernet import Fernet
import sys

def load_key():
    return open("sdds.key", "rb").read()

def decrypt_file(filename):
    key = load_key()
    fernet = Fernet(key)

    with open(filename, "rb") as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = fernet.decrypt(encrypted)

    with open("decrypted_" + filename.replace(".enc", ""), "wb") as decrypted_file:
        decrypted_file.write(decrypted)

    print(f"✅ Decrypted {filename} → decrypted_{filename.replace('.enc', '')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 decrypt_file.py <encrypted filename>")
        sys.exit(1)

    decrypt_file(sys.argv[1])
