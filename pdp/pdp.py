from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils import block_ip, check_blacklist_file, load_trust_db, save_trust_db, adjust_trust, get_network_trust
from policies import evaluate_external_net_activity, evaluate_internal_net_activity, evaluate_ip_country, evaluate_operation, evaluate_wifi_net_activity
from encrypt_existing import encrypt_trust_file
import logging


# configurazione logging
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


@app.route('/update_trust', methods=['POST'])
def update_trust():
    """
    Endpoint per aggiornare il punteggio di fiducia o bloccare un ip in base ai dati ricevuti da Splunk.
    """
    data = request.get_json()
    logging.info("Payload ricevuto da Splunk")
    
    trust_type = data.get("search_name", "")
    result = data.get("result", {})
    logging.info("Ip contenuto nel payload:")
    logging.info(result)
    results = [result] if isinstance(result, dict) else result
    
    updated_entries = []
    
    for entry in results:
        ip = entry.get("src_ip") 
        if ip:

            # Policy: TrustReputation-Increase
            if trust_type == "TrustReputation-Increase":
                logging.info("Policy: TrustReputation-Increase")
                adjust_trust(ip, +1, "Consistent benign behavior")
                updated_entries.append(ip)

            # Policy: Snort-Attack-Detection-30Days
            elif trust_type.strip() == "Snort-Attack-Detection-30Days":
                logging.info("Policy: Snort-Attack-Detection-30Days")
                block_ip(ip)  # Blocca l'IP
                updated_entries.append(ip)
            
            # Policy: Non-Working-Hours-Detection-More-Than-10-IPs
            elif trust_type == "Non-Working-Hours-Detection-More-Than-10-IPs":
                logging.info("Policy: Non-Working-Hours-Detection-More-Than-10-IPs")
                adjust_trust(ip, -15, "More than 30 anomalous accesses detected outside working hours")
                updated_entries.append(ip)

            # Policy: TrustReputation-Decrease
            elif trust_type == "TrustReputation-Decrease":
                logging.info("Policy: TrustReputation-Decrease")
                adjust_trust(ip, -40, "HTTP POST DoS Detected")
                updated_entries.append(ip)

            # Policy: PortScanning-HighRate-Detection
            elif trust_type == "PortScanning-HighRate-Detection":
                logging.info("Policy: PortScanning-HighRate-Detection")
                block_ip(ip)
                updated_entries.append(ip)
            
            # Policy: Shell-code-injection
            elif trust_type == "ShellCode-Injection-Detection":
                logging.info("Policy: ShellCode-Injection-Detection")
                block_ip(ip)
                updated_entries.append(ip)
            
            else:
                logging.warning(f"⚠️ search_name non riconosciuto: {trust_type}")
                
            
    if not updated_entries:
        logging.warning("⚠️ Nessuna voce valida trovata nel payload")

    return jsonify({"status": "received"}), 200


@app.route("/decide", methods=["POST"])
def decide():
    """
    Endpoint chiamato dal PEP (Policy Enforcement Point) per determinare se un'operazione richiesta
    da un utente debba essere consentita o negata, sulla base di:
    - indirizzo IP del client e fiducia associata
    - ruolo dell'utente
    - tipo di operazione richiesta
    - tipo di documento su cui si vuole agire

    La funzione esegue le seguenti verifiche:
    1. Controlla se l'IP è presente nella blacklist → deny immediato se lo è.
    2. Esegue valutazioni di rete personalizzate in base alla provenienza dell'IP.
    3. Ottiene il punteggio di fiducia della rete e del ruolo.
    4. Calcola il punteggio combinato.
    5. Controlla se l'operazione è compatibile col ruolo e se il punteggio è sufficiente.
    6. Restituisce una decisione finale (allow / deny) con dettagli.
    """

    logging.info("Ricezione dei dati da parte del PEP")

    data = request.json

    client_ip = data.get("client_ip")
    logging.info(f"Client IP: {client_ip}")

    role = data.get("role")
    logging.info(f"Ruolo: {role}")

    operation = data.get("operation")
    logging.info(f"Operazione: {operation}")

    document_type = data.get("document_type")
    logging.info(f"Tipo di Documento: {document_type}")

    # Verifica se l'IP è in blacklist
    logging.info("Verifico se l'IP è in blacklist")
    if check_blacklist_file(client_ip):
        logging.info(f"[PDP] IP {client_ip} presente in blacklist")
        return jsonify({
            "decision": "deny",
            "trust": "blacklisted",
            "required": "N/A",
            "operation_allowed": False
        }), 200
    else: logging.info(f"[PDP] IP {client_ip} non presente in blacklist")

    # Valutazioni aggiuntive
    logging.info("Esecuzione di valutazioni aggiuntive per la rete di provenienza della richiesta")
    evaluate_external_net_activity(client_ip)
    evaluate_internal_net_activity(client_ip)
    evaluate_wifi_net_activity(client_ip)
    evaluate_ip_country(client_ip)

    # Ottieni il punteggio di fiducia della rete
    logging.info("Ottengo fiducia della rete:")
    network_trust = get_network_trust(client_ip).get("score", 50)
    logging.info(f"Fiducia relativa a {client_ip}: {network_trust}")

    # Ottieni il punteggio di fiducia basato sul ruolo
    logging.info("Ottengo fiducia del ruolo:")
    role_trust = ROLE_BASE_TRUST.get(role, 50)  # Valore di default se ruolo non riconosciuto
    logging.info(f"Fiducia del ruolo {role}: {role_trust}")

    # Calcola il punteggio combinato
    combined_trust = (network_trust + role_trust) / 2
    logging.info(f"Punteggio combinato: {combined_trust}")

    # Se il punteggio della rete è inferiore alla soglia, aggiungi l'IP alla blacklist
    if network_trust <= 0:
        block_ip(client_ip)
        logging.info(f"[PDP] IP {client_ip} aggiunto alla blacklist per basso punteggio di rete")
        return jsonify({
            "decision": "deny",
            "trust": combined_trust,
            "required": "N/A",
            "operation_allowed": False
        }), 200

    # Ottieni la soglia richiesta per l'operazione e il tipo di documento
    min_required = OPERATION_THRESHOLDS.get(document_type, {}).get(operation)
    if min_required is None:
        return jsonify({"error": "Operazione o tipo documento non validi"}), 400
    logging.info(f"La soglia di fiducia richiesta per l'operazione {operation } per un documento di tipo {document_type} è {min_required}")

    # Verifica se l'operazione è consentita per il ruolo
    logging.info("Verifico se l'operazione è consentita per il ruolo")
    operation_allowed = evaluate_operation(role, operation)
    logging.info(f"Operation allowed: {operation_allowed}")

    # Decisione finale
    logging.info("Decisione finale:")
    if combined_trust >= min_required and operation_allowed:
        logging.info(f"Decisione finale: operation allowed")
        return jsonify({
            "decision": "allow",
            "trust": combined_trust,
            "required": min_required,
            "operation_allowed": operation_allowed
        }), 200
    else:
        logging.info(f"Decisione finale: operation denied")
        return jsonify({
            "decision": "deny",
            "trust": combined_trust,
            "required": min_required,
            "operation_allowed": operation_allowed
        }), 200

   
if __name__ == "__main__":
    trust_db = load_trust_db()
    trust_db = {}
    save_trust_db(trust_db)
    app.run(host="0.0.0.0", port=5050)