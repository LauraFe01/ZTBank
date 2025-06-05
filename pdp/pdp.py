from flask import Flask, request, jsonify
import requests
from datetime import datetime, timezone
import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from utils import block_ip, check_blacklist_file, load_trust_db, save_trust_db, reset_trust, adjust_trust, penalize_all_on_ip
from policies import evaluate_external_net_activity, evaluate_internal_net_activity, evaluate_ip_country, evaluate_operation
from encrypt_existing import encrypt_trust_file
import logging
import re


logging.basicConfig(level=logging.INFO)


# Carica la chiave dal file .env
load_dotenv()


# Dizionario di punteggi base di fiducia assegnati in base al ruolo dell'utente
ROLE_BASE_TRUST = {
    "Direttore": 85,
    "Cassiere": 70,
    "Consulente": 75,
    "Cliente": 60
}


# Soglie minime di fiducia richieste per operazioni su diversi tipi di documenti
OPERATION_THRESHOLDS = {
    "Dati Personali": {"read": 60, "write": 80, "delete": 80},
    "Dati Transazionali": {"read": 65, "write": 75, "delete": 80},
    "Documenti Operativi": {"read": 60, "write": 70, "delete": 80}
}


app = Flask(__name__)

# se la ss è fatta bene in savedsearches.conf questa non serve! Vedi Policy: TrustReputation-Increase
def extract_src_ip(entry):
    raw = entry.get("_raw", "")
    match = IP_RE.search(raw)
    return match.group(1) if match else None


@app.route('/update_trust', methods=['POST'])
def update_trust():
    """
    Endpoint per aggiornare il punteggio di fiducia o bloccare un ip in base ai dati ricevuti da Splunk.
    """
    data = request.get_json()
    logging.info("Payload ricevuto da Splunk")
    logging.info(json.dumps(data, indent=2))  # Stampa il payload ben formattato
    
    trust_type = data.get("search_name", "")


    # Policy: TrustReputation-Increase
    if trust_type == "TrustReputation-Increase":
        logging.info("Policy: TrustReputation-Increase")
        result = data.get("result", {})
        logging.info(result) # stampa le informazioni di interesse contenute nel payload (ip)

        # Normalizza in lista, anche se è un solo elemento
        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip")
            if ip:
                penalize_all_on_ip(ip, +1, "Consistent benign behavior")
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")
    

    # Policy: Snort-Attack-Detection-30Days
    elif trust_type.strip() == "Snort-Attack-Detection-30Days":
        logging.info("Policy: Snort-Attack-Detection-30Days")
        result = data.get("result", {})
        logging.info(f"result: {result}")

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = extract_src_ip(entry)
            if ip:
                block_ip(ip)  # Blocca l'IP
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")


    # Policy: Non-Working-Hours-Detection-More-Than-10-IPs
    elif trust_type == "Non-Working-Hours-Detection-More-Than-10-IPs":
        logging.info("Policy: Non-Working-Hours-Detection-More-Than-10-IPs")
        result = data.get("result", {})
        logging.info(f"result: {result}")

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = extract_src_ip(entry)
            if ip:
                penalize_all_on_ip(ip, -15, "More than 30 anomalous accesses detected outside working hours")
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")
    

    # Policy: TrustReputation-Decrease
    elif trust_type == "TrustReputation-Decrease":
        logging.info("Policy: TrustReputation-Decrease")
        result = data.get("result", {})
        logging.info(result)

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip") 
            if ip:
                logging.warning("IP-DOS: {ip}, fiducia diminuita")
                penalize_all_on_ip(ip, -40, "HTTP POST DoS Detected")
                updated_ips.append(ip)

        if not updated_ips:
            logging.warning("⚠️ Nessun IP valido trovato nel payload")


    # Policy: PortScanning-HighRate-Detection
    elif trust_type == "PortScanning-HighRate-Detection":
        logging.info("Policy: PortScanning-HighRate-Detection")
        result = data.get("result", {})
        logging.info(result)

        results = [result] if isinstance(result, dict) else result

        updated_ips = []

        for entry in results:
            ip = entry.get("src_ip") 
            if ip:
                logging.warning("IP-PORT-SCANNING: {ip}, blocco automatico")
                block_ip(ip)
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
    username = data.get("username")
    document_type = data.get("document_type")
    check = True

    trust_key = f"{username}|{client_ip}"
    logging.info(f"[PDP] Valuto {operation.upper()} su {document_type} da {role}")

    if check_blacklist_file(client_ip):
        logging.info("[PDP] IP %s presente in blacklist", client_ip)
        adjust_trust(client_ip, -30, "IP in static blacklist (file)")

    # 🧾 Inizializza se non esiste ancora
    if trust_key not in trust_db:
        base = ROLE_BASE_TRUST.get(role, 100)
        trust_db[trust_key] = {
            "score": base,
            "last_seen": datetime.now().isoformat(),
            "last_reason": "Ruolo iniziale: " + role
        }
        logging.info(f"Trust db aggiornato con aggiunta di un utente {trust_db}")
        save_trust_db(trust_db)
    
    evaluate_external_net_activity(trust_key)
    evaluate_internal_net_activity(trust_key)
    evaluate_ip_country(trust_key)
    if operation != "read":
        check = evaluate_operation(role, operation)
        logging.info(f"CHECK {check}")

    score = trust_db[trust_key]["score"]
    min_required = OPERATION_THRESHOLDS.get(document_type, {}).get(operation)
    logging.info(f"TRUST SCORE {score}")

    if min_required is None:
        return jsonify({"error": "Operazione o tipo documento non validi"}), 400
    logging.info(f"[PDP] Trust: {score} / Soglia richiesta: {min_required}")
    if score >= min_required and check:
        logging.info("qui")
        return jsonify({
        "decision": "allow",
        "trust": score,
        "required": min_required,
        "operation_allowed": check
        }), 200

    else:
        return jsonify({
        "decision": "deny",
        "trust": score,
        "required": min_required,
        "operation_allowed": check
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
   

if __name__ == "__main__":
    trust_db = load_trust_db()
    trust_db = {}
    logging.info(f"DB iniziale: {trust_db}")
    save_trust_db(trust_db)

    app.run(host="0.0.0.0", port=5050)