import os
import json
import logging
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

fernet = Fernet(KEY.encode())
USER_DB_FILE = "users_db.json"

def load_user_db():
    """
    Carica il database utenti dal file cifrato.

    Il file viene decifrato utilizzando la chiave specificata tramite variabile 
    d'ambiente. In caso di errore o file mancante, restituisce un dizionario vuoto.

    Returns:
        dict: Il contenuto del database utenti, oppure un dizionario vuoto se non leggibile.
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
    Salva il database utenti in formato cifrato.

    Il contenuto viene serializzato in JSON, cifrato con Fernet e scritto su disco.

    Args:
        user_db (dict): Il database degli utenti da salvare.
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
    Crea un nuovo utente nel database.

    Verifica se l'utente esiste già. In caso contrario, la password viene hashata 
    con bcrypt e l'utente viene aggiunto al database.

    Args:
        username (str): Nome utente.
        password (str): Password in chiaro.
        role (str): Ruolo dell'utente.
        user_db (dict): Database utenti corrente.

    Returns:
        tuple: (bool, str) Esito dell'operazione e messaggio descrittivo.
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
    Verifica le credenziali di accesso di un utente.

    Controlla se l'utente esiste e se la password fornita corrisponde 
    all'hash memorizzato.

    Args:
        username (str): Nome utente.
        password (str): Password da verificare.
        user_db (dict): Database utenti corrente.

    Returns:
        tuple: (bool, str) True e ruolo utente se autenticazione riuscita,
               False e messaggio di errore altrimenti.
    """
    user = user_db.get(username)
    if not user:
        return False, "Utente non trovato"

    if bcrypt.checkpw(password.encode(), user["password"].encode()):
        return True, user["role"]
    else:
        return False, "Password errata"
