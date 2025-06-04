import os
import json
import logging
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Config
load_dotenv()
KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

fernet = Fernet(KEY.encode())
USER_DB_FILE = "users_db.json"

# --- Utility ---

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "rb") as f:
                encrypted = f.read()
            decrypted = fernet.decrypt(encrypted)
            return json.loads(decrypted)
        except Exception as e:
            logging.warning(f"[AUTH] Errore lettura DB utenti: {e}")
            return {}
    return {}

def save_user_db(user_db):
    try:
        raw = json.dumps(user_db).encode()
        encrypted = fernet.encrypt(raw)
        with open(USER_DB_FILE, "wb") as f:
            f.write(encrypted)
        logging.info("[AUTH] DB utenti salvato.")
    except Exception as e:
        logging.warning(f"[AUTH] Errore salvataggio DB utenti: {e}")

def create_user(username, password, role, user_db):
    if username in user_db:
        return False, "Utente già esistente"
    
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_db[username] = {
        "password": hashed_pw,
        "role": role
    }
    save_user_db(user_db)
    return True, "Utente creato con successo"

def authenticate_user(username, password, user_db):
    user = user_db.get(username)
    if not user:
        return False, "Utente non trovato"

    if bcrypt.checkpw(password.encode(), user["password"].encode()):
        return True, user["role"]
    else:
        return False, "Password errata"
