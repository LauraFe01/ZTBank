from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from splunk_methods import splunk_search
from utils import block_ip, check_blacklist_file, load_trust_db, save_trust_db, reset_trust, adjust_trust
from policies import evaluate_external_net_activity, evaluate_internal_net_activity, evaluate_ip_country
from encrypt_existing import encrypt_trust_file
import logging
import re

logging.basicConfig(level=logging.INFO)

# Carica la chiave dal file .env
load_dotenv()

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

app = Flask(__name__)

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

# attraverso questa rotta il PDP riceve i dati dal PEP e valuta la fiducia e se l'accesso è consentito o meno
@app.route("/decide", methods=["POST"])
def decide():
    trust_db=load_trust_db()  # ✅ Assicurati che trust_db sia aggiornato

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
        base = ROLE_BASE_TRUST.get(role, 100)
        trust_db[client_ip] = {
            "score": base,
            "last_seen": datetime.now().isoformat(),
            "last_reason": "Ruolo iniziale: " + role
        }
        save_trust_db()

    evaluate_external_net_activity(client_ip)
    evaluate_internal_net_activity(client_ip)
    evaluate_ip_country(client_ip)

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
    trust_db = load_trust_db()
    now = datetime.datetime.now()
    for ip, data in trust_db.items():
        last_seen = datetime.datetime.fromisoformat(data["last_seen"])
        delta = now - last_seen
        if delta.days >= 60:
            adjust_trust(ip, +5, "No incidents in 60+ days")
    
    return jsonify({"status": "rewards applied"}), 200

@app.route("/dump", methods=["GET"])
def dump():
    trust_db = load_trust_db()
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
    trust_db = load_trust_db()
    trust_db = reset_trust(trust_db)
    logging.info(f"DB iniziale: {trust_db}")
    save_trust_db(trust_db)

    app.run(host="0.0.0.0", port=5050)