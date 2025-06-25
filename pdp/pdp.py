from flask import Flask, request, jsonify
from dotenv import load_dotenv
from utils import block_ip, check_blacklist_file, load_trust_db, save_trust_db, adjust_trust, get_network_trust
from policies import evaluate_external_net_activity, evaluate_internal_net_activity, evaluate_ip_country, evaluate_operation, evaluate_wifi_net_activity, evaluate_data
from encrypt_existing import encrypt_trust_file
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

ROLE_BASE_TRUST = {
    "Direttore": 85,
    "Cassiere": 70,
    "Consulente": 75,
    "Cliente": 60
}

OPERATION_THRESHOLDS = {
    "Dati Personali": {"read": 60, "write": 80, "delete": 80},
    "Dati Transazionali": {"read": 65, "write": 75, "delete": 80},
    "Documenti Operativi": {"read": 60, "write": 70, "delete": 80}
}

app = Flask(__name__)


@app.route('/update_trust', methods=['POST'])
def update_trust():
    """
    Endpoint per l'aggiornamento della fiducia o il blocco di un IP
    in base a dati ricevuti da Splunk.

    Analizza il tipo di evento (`search_name`) e applica la policy corrispondente:
    - Può aumentare o diminuire il punteggio di fiducia di un IP.
    - Può bloccare un IP, aggiungendolo alla blacklist.
    - Supporta eventi multipli tramite array JSON nel campo `result`.

    Returns:
        Response JSON con stato di ricezione (always 200 OK).
    """
    data = request.get_json()
    trust_type = data.get("search_name", "")
    result = data.get("result", {})
    results = [result] if isinstance(result, dict) else result
    updated_entries = []

    for entry in results:
        ip = entry.get("src_ip")
        if ip:
            if trust_type == "TrustReputation-Increase":
                logging.info("Policy: TrustReputation-Increase")
                adjust_trust(ip, +1, "Consistent benign behavior")
                updated_entries.append(ip)

            elif trust_type.strip() == "Snort-Attack-Detection-30Days":
                logging.info("Policy: Snort-Attack-Detection-30Days")
                block_ip(ip)
                updated_entries.append(ip)

            elif trust_type == "Non-Working-Hours-Detection-More-Than-10-IPs":
                logging.info("Policy: Non-Working-Hours-Detection-More-Than-10-IPs")
                adjust_trust(ip, -15, "More than 30 anomalous accesses detected outside working hours")
                updated_entries.append(ip)

            elif trust_type == "TrustReputation-Decrease":
                logging.info("Policy: TrustReputation-Decrease")
                adjust_trust(ip, -40, "HTTP POST DoS Detected")
                updated_entries.append(ip)

            elif trust_type == "PortScanning-HighRate-Detection":
                logging.info("Policy: PortScanning-HighRate-Detection")
                block_ip(ip)
                updated_entries.append(ip)

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
    Endpoint per valutare l'autorizzazione di un'operazione richiesta da un utente.

    Analizza i seguenti fattori per prendere una decisione:
    - IP del client (e blacklist)
    - Fiducia di rete
    - Fiducia basata sul ruolo
    - Tipo di operazione e documento
    - Compatibilità tra ruolo e tipo di risorsa

    Se i criteri minimi di fiducia sono soddisfatti e l'accesso è autorizzato,
    restituisce "allow", altrimenti "deny".

    Returns:
        Response JSON contenente la decisione, il punteggio di fiducia, la soglia richiesta
        e se l'operazione è ammessa.
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

    logging.info("Verifico se l'IP è in blacklist")
    if check_blacklist_file(client_ip):
        logging.info(f"[PDP] IP {client_ip} presente in blacklist")
        return jsonify({
            "decision": "deny",
            "trust": "blacklisted",
            "required": "N/A",
            "operation_allowed": False
        }), 200
    else:
        logging.info(f"[PDP] IP {client_ip} non presente in blacklist")

    logging.info("Ottengo fiducia della rete pre processamento:")
    network_trust = get_network_trust(client_ip).get("score", 50)
    logging.info(f"Fiducia relativa a {client_ip}: {network_trust}")

    logging.info("Esecuzione di valutazioni aggiuntive per la rete di provenienza della richiesta")
    evaluate_external_net_activity(client_ip)
    evaluate_internal_net_activity(client_ip)
    evaluate_wifi_net_activity(client_ip)
    evaluate_ip_country(client_ip)

    logging.info("Ottengo fiducia della rete:")
    network_trust = get_network_trust(client_ip).get("score", 50)
    logging.info(f"Fiducia relativa a {client_ip}: {network_trust}")

    logging.info("Ottengo fiducia del ruolo:")
    role_trust = ROLE_BASE_TRUST.get(role, 50)
    logging.info(f"Fiducia del ruolo {role}: {role_trust}")

    combined_trust = (network_trust + role_trust) / 2
    logging.info(f"Punteggio combinato: {combined_trust}")

    if network_trust <= 0:
        block_ip(client_ip)
        logging.info(f"[PDP] IP {client_ip} aggiunto alla blacklist per basso punteggio di rete")
        return jsonify({
            "decision": "deny",
            "trust": combined_trust,
            "required": "N/A",
            "operation_allowed": False
        }), 200

    min_required = OPERATION_THRESHOLDS.get(document_type, {}).get(operation)
    if min_required is None:
        return jsonify({"error": "Operazione o tipo documento non validi"}), 400

    logging.info(f"La soglia di fiducia richiesta per l'operazione {operation} per un documento di tipo {document_type} è {min_required}")

    logging.info("Verifico se l'operazione è consentita per il ruolo")
    operation_allowed = evaluate_operation(role, operation)
    logging.info(f"Operation allowed: {operation_allowed}")

    logging.info("Verifico se l'utente ha permesso di accedere al tipo di documento richiesto")
    resource_allowed = evaluate_data(role, document_type)
    logging.info(f"Resource allowed: {resource_allowed}")

    logging.info("Decisione finale:")
    if combined_trust >= min_required and operation_allowed and resource_allowed:
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
