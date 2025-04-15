import json, os
from datetime import datetime, timedelta

def check_and_delete(meta_file):
    with open(meta_file, "r") as f:
        metadata = json.load(f)

    created_time = datetime.strptime(metadata["created_at"], "%Y-%m-%d %H:%M:%S")
    expire_in = int(metadata["expire_in"])
    expiry_time = created_time + timedelta(seconds=expire_in)

    if datetime.now() >= expiry_time:
        try:
            os.remove(metadata["filename"])
            os.remove(meta_file)
            print(f"🗑️ Deleted {metadata['filename']}")
        except:
            print(f"⚠️ Failed to delete {metadata['filename']}")

# Run for all .meta files
for file in os.listdir():
    if file.endswith(".meta"):
        check_and_delete(file)
