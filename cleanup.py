import os
import time

UPLOAD_FOLDER = 'uploads'
MAX_FILE_AGE_SECONDS = 3600  # 1 hour = 3600 seconds. You can change to 86400 for 1 day

now = time.time()
deleted = 0

for filename in os.listdir(UPLOAD_FOLDER):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.isfile(file_path):
        file_age = now - os.path.getmtime(file_path)
        if file_age > MAX_FILE_AGE_SECONDS:
            os.remove(file_path)
            deleted += 1
            print(f"🗑️ Deleted {filename} (age: {int(file_age)}s)")

if deleted == 0:
    print("✅ No old files found to delete.")
else:
    print(f"✅ Cleanup complete. {deleted} file(s) deleted.")
