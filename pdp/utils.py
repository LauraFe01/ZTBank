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


def reset_trust(trust_db):
    for ip in list(trust_db.keys()):  # Crea copia delle chiavi per evitare errori
        if ip == "172.24.0.2" or ip == "172.21.0.1":
            del trust_db[ip]  # ❌ IP indesiderati: li elimini
        else:
            trust = trust_db[ip]
            trust["score"] = 100
            trust["last_reason"] = "Reset globale"
            trust["last_seen"] = datetime.now().isoformat()
    logging.info("[PDP] Reset completato. IP esclusi: 172.24.0.2, 172.21.0.1")
    return trust_db


def penalize_all_on_ip(ip, delta, reason):

    trust_db = load_trust_db()
    updated = 0

    for trust_key in trust_db:
        if trust_key.endswith(f"|{ip}"):
            trust = trust_db[trust_key]
            trust["score"] = max(0, trust["score"] + delta)
            trust["last_seen"] = datetime.now().isoformat()
            trust["last_reason"] = reason
            updated += 1
            logging.info(f"[PDP] 🔻 Penalizzato {trust_key} → {trust['score']}")

    if updated > 0:
        save_trust_db(trust_db)
        logging.info(f"[PDP] Penalizzati {updated} utenti su IP {ip}")
    else:
        logging.info(f"[PDP] Nessun utente trovato per IP {ip}")


def adjust_trust(trust_key, change, reason):
    logging.info(f"[PDP] Dentro ADJUST: {trust_key}, {change}, {reason}")
    trust_db = load_trust_db()
    
    now = datetime.now(timezone.utc).isoformat()
    trust = trust_db.get(trust_key, {
        "score": 100,
        "last_seen": now,
        "last_reason": "Initial trust level"
    })


    trust["score"] = max(0, min(100, trust["score"] + change))
    trust["last_seen"] = now
    trust["last_reason"] = reason
    trust_db[trust_key] = trust

    logging.info(f"[PDP] 🎉 Trust per {trust_key} aggiornata a {trust['score']} ({reason})")
    save_trust_db(trust_db)

    if trust["score"] <= BLACKLIST_THRESHOLD:
        ip = trust_key.split("|")[1]
        logging.warning(f"[PDP] IP {trust_key} ha fiducia bassa ({trust['score']}) → blacklist")
        block_ip(ip)

    return trust_db
