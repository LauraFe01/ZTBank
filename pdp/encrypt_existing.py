import json, os
from cryptography.fernet import Fernet

TRUST_FILE = "trust_db.json"

with open(TRUST_FILE, "r") as f:
    data = json.load(f)

key = os.environ["TRUST_KEY"].encode()
fernet = Fernet(key)

encrypted = fernet.encrypt(json.dumps(data).encode())

with open(TRUST_FILE, "wb") as f:
    f.write(encrypted)

print("✅ File cifrato con successo.")
