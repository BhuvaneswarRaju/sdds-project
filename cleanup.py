import os
import time

UPLOAD_FOLDER = 'uploads'
EXPIRATION_SECONDS = 86400  # 24 hours

now = time.time()
deleted = 0

# Create folder if not exists (just in case)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

for filename in os.listdir(UPLOAD_FOLDER):
    if filename.endswith('.enc'):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            file_age = now - os.path.getmtime(file_path)
            if file_age > EXPIRATION_SECONDS:
                os.remove(file_path)
                deleted += 1
                print(f"🧹 Deleted {filename} (age: {int(file_age)}s)")
        except Exception as e:
            print(f"⚠️ Could not delete {filename}: {e}")

if deleted == 0:
    print("✅ No expired files found.")
else:
    print(f"✅ Cleanup complete. {deleted} file(s) deleted.")
