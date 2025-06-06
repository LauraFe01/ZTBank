import os
import json
import logging
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv


# Configurazione
load_dotenv()
KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

fernet = Fernet(KEY.encode())
USER_DB_FILE = "users_db.json"


# --- Utility ---


def load_user_db():
    """
    Carica il database degli utenti dal file cifrato.
    Se il file non esiste o si verifica un errore, restituisce un dizionario vuoto.
    """
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
    """
    Salva il database degli utenti nel file, cifrandolo.
    """
    try:
        raw = json.dumps(user_db).encode()
        encrypted = fernet.encrypt(raw)
        with open(USER_DB_FILE, "wb") as f:
            f.write(encrypted)
        logging.info("[AUTH] DB utenti salvato.")
    except Exception as e:
        logging.warning(f"[AUTH] Errore salvataggio DB utenti: {e}")


def create_user(username, password, role, user_db):
    """
    Crea un nuovo utente con username, password e ruolo specificati.
    La password viene hashata con bcrypt.
    Se l'utente esiste già, restituisce False e un messaggio.
    Altrimenti, aggiunge l'utente al database e restituisce True e un messaggio di successo.
    """
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
    """
    Autentica un utente verificando username e password.
    Se l'autenticazione ha successo, restituisce True e il ruolo dell'utente.
    Altrimenti, restituisce False e un messaggio di errore.
    """
    user = user_db.get(username)
    if not user:
        return False, "Utente non trovato"

    if bcrypt.checkpw(password.encode(), user["password"].encode()):
        return True, user["role"]
    else:
        return False, "Password errata"
