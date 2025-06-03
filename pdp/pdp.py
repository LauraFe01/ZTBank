from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from splunk_methods import splunk_search
import logging
import re
import ipaddress
import time

logging.basicConfig(level=logging.INFO)

# Carica la chiave dal file .env
load_dotenv()
KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

fernet = Fernet(KEY.encode())
app = Flask(__name__)

TRUST_FILE = "trust_db.json"
trust_db = {}
DEFAULT_TRUST = 100

ROLE_BASE_TRUST = {
    "Direttore": 85,
    "Cassiere": 70,
    "Consulente": 75,
    "Cliente": 60
}

OPERATION_THRESHOLDS = {
    "Dati Personali": {"read": 60, "write": 80},
    "Dati Transazionali": {"read": 65, "write": 75},
    "Documenti Operativi": {"read": 60, "write": 70}
}

# --- Persistenza ---

def load_trust_db():
    global trust_db
    if os.path.exists(TRUST_FILE):
        try:
            with open(TRUST_FILE, "rb") as f:
                encrypted = f.read()
            raw = fernet.decrypt(encrypted)
            trust_db.update(json.loads(raw))
            logging.info("[PDP] trust_db caricato da file cifrato.")
            logging.info("Trust DB (decifrato):\n%s", json.dumps(trust_db, indent=2))
        except Exception as e:
            logging.info(f"[PDP] ⚠️ Errore nella decifratura del trust_db: {e}")
    else:
        logging.info("[PDP] ⚠️ Nessun trust_db.json trovato, uso database vuoto.")


def save_trust_db():
    try:
        raw = json.dumps(trust_db).encode()
        encrypted = fernet.encrypt(raw)
        with open(TRUST_FILE, "wb") as f:
            f.write(encrypted)
        logging.info("[PDP] trust_db salvato su file cifrato.")
    except Exception as e:
        logging.info(f"[PDP] ⚠️ Errore nella cifratura del trust_db: {e}")

# --- Logica trust ---

def adjust_trust(ip, change, reason):
    global trust_db
    now = datetime.now(timezone.utc).isoformat()
    load_trust_db()
    trust = trust_db.get(ip)

    # Se non esiste ancora, inizializzalo
    if trust is None:
        trust = {
            "score": 100,  # oppure altro valore iniziale
            "last_seen": now,
            "last_reason": "Initial trust level"
        }
        trust_db[ip] = trust
        logging.info(f"[PDP] Trust inizializzata per {ip} a {trust['score']}")

    trust["score"] = max(0, min(100, trust["score"] + change))
    trust["last_seen"] = now
    trust["last_reason"] = reason
    trust_db[ip] = trust

    logging.info(f"[PDP] 🎉 Trust per {ip} aggiornata a {trust['score']} ({reason})")
    save_trust_db()

""" @app.route('/update_trust', methods=['POST'])
def update_trust():
    data = request.get_json()
    logging.info("✅ Payload ricevuto da Splunk:")
    logging.info(f"[PDP] payload : {data} ")

    raw = data.get("result", {}).get("_raw", "")
    trust_type = data.get("search_name", "")
    
    # Regex: IP address (3rd field del log squid)
    match = re.search(r"\d+\.\d+\.\d+\.\d+", raw)

    logging.info(f"[PDP] indirizzo IP : {match} ")
    
    if match:
        ip = match.group()
        logging.info(f"✅ IP sorgente estratto: {ip}")

        if trust_type == "blacklist":
            ips = data.get("ips", "").split()
            for ip in ips:
                adjust_trust(ip, -30, "Blacklist match")

        elif trust_type == "attack":
            count = int(data.get("count", 0))
            if count > 10:
                adjust_trust(ip, -30, f"{count} attacks detected")

        elif trust_type == "anomaly":
            count = int(data.get("count", 0))
            if count > 30:
                adjust_trust(ip, -20, f"{count} anomalous accesses")
        
        elif trust_type == "External-Net-Detection":
            logging.info(f"Individuata una external request")
            adjust_trust(ip, -20, f"External net access")
    
    else:
        print("❌ Nessun IP trovato nel campo _raw.")


    # Risposta al chiamante (Splunk)
    return jsonify({"status": "received"}), 200 """

@app.route('/update_trust', methods=['POST'])
def update_trust():
    data = request.get_json()
    logging.info("Payload ricevuto da Splunk")
    #logging.info(json.dumps(data, indent=2))  # Stampa il payload ben formattato

    trust_type = data.get("search_name", "")

    # Policy: TrustReputation-Increase
    if trust_type == "TrustReputation-Increase":
        result = data.get("result", {})
        logging.info(result) # stampa le informazioni di interesse contenute nel payload (ip)

        # Normalizza in lista, anche se è un solo elemento
        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip") 
            if ip:
                adjust_trust(ip, +1, "Consistent benign behavior")
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")
    else:
        logging.warning(f"⚠️ search_name non riconosciuto: {trust_type}")

    return jsonify({"status": "received"}), 200


# toglie 10 punti di fiducia nel caso di richieste proveniente da reti esterne
def evaluate_external_net_activity(ip):
    if ipaddress.IPv4Address(ip) not in ipaddress.IPv4Network("172.20.0.0/24"):
        adjust_trust(ip, -20, "External net detected")

# aggiunge 10 punti di fiducia nel caso di richieste provenienti da reti interne
def evaluate_internal_net_activity(ip):
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.20.0.0/16"):
        adjust_trust(ip, +10, "Internal net access")

# attraverso questa rotta il PDP riceve i dati dal PEP e valuta la fiducia e se l'accesso è consentito o meno
@app.route("/decide", methods=["POST"])
def decide():
    data = request.json
    client_ip = data.get("client_ip")
    role = data.get("role")
    operation = data.get("operation")
    document_type = data.get("document_type")

    logging.info(f"[PDP] Valuto {operation.upper()} su {document_type} da {role}")

    # Inizializza se non esiste
    if client_ip not in trust_db:
        base = ROLE_BASE_TRUST.get(role, DEFAULT_TRUST)
        trust_db[client_ip] = {
            "score": base,
            "last_seen": datetime.datetime.now().isoformat(),
            "last_reason": "Ruolo iniziale: " + role
        }
        save_trust_db()

    evaluate_external_net_activity(client_ip)
    evaluate_internal_net_activity(client_ip)

    score = trust_db[client_ip]["score"]
    min_required = OPERATION_THRESHOLDS.get(document_type, {}).get(operation)

    if min_required is None:
        return jsonify({"error": "Operazione o tipo documento non validi"}), 400

    decision = "allow" if score >= min_required else "deny"

    logging.info(f"[PDP] Trust: {score} / Soglia richiesta: {min_required} → Decisione: {decision}")

    return jsonify({
        "decision": decision,
        "trust": score,
        "required": min_required
    }), 200


@app.route("/reward_check", methods=["POST"])
def reward_check():
    now = datetime.datetime.now()
    for ip, data in trust_db.items():
        last_seen = datetime.datetime.fromisoformat(data["last_seen"])
        delta = now - last_seen
        if delta.days >= 60:
            adjust_trust(ip, +5, "No incidents in 60+ days")
    return jsonify({"status": "rewards applied"}), 200

@app.route("/dump", methods=["GET"])
def dump():
    return jsonify(trust_db)

if __name__ == "__main__":
    load_trust_db()
    app.run(host="0.0.0.0", port=5050)