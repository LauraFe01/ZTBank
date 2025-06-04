from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from splunk_methods import splunk_search
from utils import block_ip, check_blacklist_file
from encrypt_existing import encrypt_trust_file
import logging
import re
import ipaddress
import geoip2.database
import time

logging.basicConfig(level=logging.INFO)

# Carica la chiave dal file .env
load_dotenv()
KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

BLACKLIST_THRESHOLD = 0
fernet = Fernet(KEY.encode())
app = Flask(__name__)

TRUST_FILE = "trust_db.json"
trust_db = {}
DEFAULT_TRUST = 100

# Carica il database GeoLite (devi scaricarlo prima)
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
geo_reader = geoip2.database.Reader(GEOIP_DB_PATH)

fernet = Fernet(KEY.encode())
app = Flask(__name__)

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

def reset_trust():
    global trust_db
    for ip in trust_db:
        trust_db[ip]["score"] = 100
        trust_db[ip]["last_reason"] = "Reset globale"
        trust_db[ip]["last_seen"] = datetime.now().isoformat()
    save_trust_db()
    logging.info("[PDP] Tutti i punteggi di fiducia sono stati resettati a 100.")

# --- Logica trust ---

def adjust_trust(ip, change, reason):
    logging.info(f"[PDP] Dentro ADJUST: {ip}, {change}, {reason}")
    global trust_db
    load_trust_db()
    
    now = datetime.now(timezone.utc).isoformat()
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

    if trust["score"] <= BLACKLIST_THRESHOLD:
        logging.warning(f"[PDP] IP {ip} ha fiducia bassa ({trust['score']}) → blacklist")
        block_ip(ip)
    save_trust_db()

def evaluate_strange_activity(ip, timestamp):
    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    hour = dt.hour
    logging.info(f"🕒 Orario accesso: {hour}")

    # Geolocalizzazione IP
    try:
        response = geo_reader.country(ip)
        country = response.country.name
        logging.info(f"🌍 Accesso da: {country}")
        if country != "Italy":
            adjust_trust(ip, -40, f"Connessione da paese esterno: {country}")
    except Exception as e:
        logging.warning(f"❗ Impossibile geolocalizzare IP {ip}: {e}")

    # Rilevamento rete interna
    if ipaddress.IPv4Address(ip) not in ipaddress.IPv4Network("172.20.0.0/24"):
        adjust_trust(ip, -5, "Rete esterna rilevata")

    # Rilevamento orario notturno DA TOGLIERE VIENE BLOCCATO DA SQUID
    if hour < 7 or hour >= 20:
        adjust_trust(ip, -10, "Accesso notturno rilevato")

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
    elif trust_type == "Snort-Attack-Detection-30Days":
        result = data.get("result", {})
        logging.info(result)

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip") 
            if ip:
                adjust_trust(ip, -25, "More than 10 attacks detected in the last 30 days")
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")
    elif trust_type == "Non-Working-Hours-Detection-More-Than-10-IPs":
        result = data.get("result", {})
        logging.info(result)

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip") 
            if ip:
                adjust_trust(ip, -15, "More than 30 anomalous accesses detected outside working hours")
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")

    elif trust_type == "TrustReputation-Decrease":
        result = data.get("result", {})
        logging.info(result)

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip") 
            if ip:
                logging.warning("IP-DOS: {ip}, fiducia diminuita")
                adjust_trust(ip, -40, "HTTP POST DoS Detected")
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
    load_trust_db()  # ✅ Assicurati che trust_db sia aggiornato

    data = request.json
    client_ip = data.get("client_ip")
    role = data.get("role")
    operation = data.get("operation")
    document_type = data.get("document_type")

    logging.info(f"[PDP] Valuto {operation.upper()} su {document_type} da {role}")

    if check_blacklist_file(client_ip):
        logging.info("[PDP] IP %s presente in blacklist", client_ip)
        adjust_trust(client_ip, -30, "IP in static blacklist (file)")

    # 🧾 Inizializza se non esiste ancora
    if client_ip not in trust_db:
        base = ROLE_BASE_TRUST.get(role, DEFAULT_TRUST)
        trust_db[client_ip] = {
            "score": base,
            "last_seen": datetime.now().isoformat(),
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

@app.route("/block_ip", methods=["POST"])
def snort_alert():
    data = request.get_json()
    logging.info("✅ Payload ricevuto da Splunk:")
    logging.info(f"[PDP] payload : {data} ")

    raw = data.get("result", {}).get("_raw", "")
    
    # Regex: IP address (3rd field del log squid)
    match = re.search(r"\d+\.\d+\.\d+\.\d+", raw)

    logging.info(f"[PDP] indirizzo IP : {match} ")
    
    if match:
        ip = match.group()
        logging.info(f"✅ IP sorgente estratto: {ip}")
        
    logging.info(f"[PDP] Allarme Snort ricevuto: {data}")

    if not ip:
        return jsonify({"error": "IP mancante"}), 400

    # Diminuisci il trust di 200 punti
    logging.info(f"Indirizzo ip che ha fatt DoS: {ip}")
    adjust_trust(ip, -200, "DoS detect")

    return jsonify({"status": "trust updated", "ip": ip}), 200


if __name__ == "__main__":
    #reset_trust()
    #encrypt_trust_file()
    load_trust_db()
    app.run(host="0.0.0.0", port=5050)