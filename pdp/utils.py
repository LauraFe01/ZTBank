import os
import subprocess
import logging
from datetime import datetime, timezone
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv


load_dotenv()
KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

fernet = Fernet(KEY.encode())
TRUST_FILE = "trust_db.json"
BLACKLIST_THRESHOLD = 0
BLACKLIST_FILE = "/app/data/blacklist/blacklist.txt"


def block_ip(ip):
    try:
        with open(BLACKLIST_FILE, "a") as f:
            f.write(f"{ip}\n")
        logging.warning(f"[PDP] IP {ip} aggiunto alla blacklist condivisa.")
    except Exception as e:
        logging.error(f"[PDP] Errore scrittura blacklist: {e}")


def check_blacklist_file(ip):
    logging.info(f"[PDP] Controllo blacklist per l'IP: {ip}")
    blacklist_path = "data/blacklist/blacklist.txt"
    if not os.path.exists(blacklist_path):
        logging.warning("Blacklist file non trovato.")
        return False
    with open(blacklist_path, "r") as f:
        blacklisted_ips = set(line.strip() for line in f if line.strip())
    return ip in blacklisted_ips


def load_trust_db():
    if os.path.exists(TRUST_FILE):
        try:
            with open(TRUST_FILE, "rb") as f:
                encrypted = f.read()
            raw = fernet.decrypt(encrypted)
            trust_db = json.loads(raw)
            logging.info("[PDP] trust_db caricato da file cifrato.")
            logging.info("Trust DB (decifrato):\n%s", json.dumps(trust_db, indent=2))
            return trust_db
        except Exception as e:
            logging.warning(f"[PDP] ⚠️ Errore nella decifratura del trust_db: {e}")
            return {}
    else:
        logging.info("[PDP] ⚠️ Nessun trust_db.json trovato, uso database vuoto.")
        return {}


def save_trust_db(trust_db):
    try:
        raw = json.dumps(trust_db).encode()
        encrypted = fernet.encrypt(raw)
        with open(TRUST_FILE, "wb") as f:
            f.write(encrypted)
        logging.info("[PDP] trust_db salvato su file cifrato.")
    except Exception as e:
        logging.warning(f"[PDP] ⚠️ Errore nella cifratura del trust_db: {e}")



def adjust_trust(ip, change, reason):
    logging.info(f"[PDP] Dentro ADJUST: {ip}, {change}, {reason}")
    trust_db = load_trust_db()

    now = datetime.now(timezone.utc).isoformat()
    trust = trust_db.get(ip)

    if trust is None:
        score = max(0, min(100, 100 + change))
        trust = {
            "score": score,
            "last_seen": now,
            "last_reason": "Initial trust level"
        }
        logging.info(f"[PDP] Trust inizializzata per {ip} a {trust['score']}")
    
    else:
        trust["score"] = max(0, min(100, trust["score"] + change))
        trust["last_seen"] = now
        trust["last_reason"] = reason

    trust_db[ip] = trust

    logging.info(f"[PDP] 🎉 Trust per {ip} aggiornata a {trust['score']} ({reason})")
    save_trust_db(trust_db)

    if trust["score"] <= BLACKLIST_THRESHOLD:
        logging.warning(f"[PDP] IP {ip} ha fiducia bassa ({trust['score']}) → blacklist")
        block_ip(ip)

    return trust_db


def get_network_trust(ip):
    """
    Restituisce il punteggio di fiducia associato a un IP o rete specifica.
    """
    trust_db = load_trust_db()
    return trust_db.get(ip)

