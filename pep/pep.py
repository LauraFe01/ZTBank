import os
from user_auth import load_user_db, authenticate_user
from flask import Flask, request, jsonify, session
import requests
import psycopg2
import logging
import pytz
from datetime import datetime
from db_scripts.db_exec import execute_single_operation, execute_write_operation

app = Flask(__name__)
app.secret_key = os.getenv("PEP_SECRET_KEY")
PDP_URL = "http://pdp:5050/decide"
logging.basicConfig(level=logging.INFO)
rome = pytz.timezone("Europe/Rome")

@app.route("/login", methods=["POST"])
def login():
    """
    Endpoint per l'autenticazione dell'utente.

    Riceve username e password via JSON, autentica l'utente tramite il database
    e in caso di successo avvia una sessione persistente.

    Returns:
        JSON response con stato dell'autenticazione (200 se ok, 401 altrimenti).
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user_db = load_user_db()
    success, role_or_msg = authenticate_user(username, password, user_db)
    if not success:
        return jsonify({"status": "error", "message": role_or_msg}), 401

    session.permanent = True
    session["username"] = username
    session["role"] = role_or_msg
    return jsonify({"status": "ok", "message": "Login riuscito"}), 200

@app.route("/logout", methods=["POST"])
def logout():
    """
    Endpoint per terminare la sessione utente.

    Cancella la sessione corrente e restituisce una conferma.

    Returns:
        JSON response con conferma di logout.
    """
    session.clear()
    return jsonify({"status": "ok", "message": "Logout effettuato"}), 200

@app.route("/request", methods=["POST"])
def handle_request():
    """
    Endpoint principale del PEP (Policy Enforcement Point) per la gestione di richieste.

    Valida l'autenticazione dell'utente, raccoglie i parametri dell'operazione e 
    inoltra la richiesta al PDP per autorizzazione. Se autorizzata, esegue l'operazione.

    Returns:
        JSON response con esito dell'autorizzazione e dell'operazione (200, 403 o 500).
    """
    logging.info("Richiesta ricevuta all'endpoint /request")
    logging.info(f"Headers: {request.headers}")
    logging.info(f"Corpo della richiesta: {request.get_data()}")
    data = request.get_json()
    logging.info(f"Dati JSON ricevuti: {data}")

    if "username" not in session or "role" not in session:
        return jsonify({"error": "Utente non autenticato"}), 401

    role = session["role"]
    logging.info(f"Ruolo dell'utente: {role}")

    username = session["username"]
    logging.info(f"Username dell'utente: {username}")

    timestamp = datetime.now(rome).strftime("%Y-%m-%d %H:%M:%S")
    operation = data.get("operation", "")
    logging.info(f"Operazione: {operation}")

    document_type = data.get("document_type", "")
    logging.info(f"Tipo di documento: {document_type}")

    nome_file = data.get("nome_file", "")
    logging.info(f"Nome del file: {nome_file}")

    contenuto = data.get("contenuto", "")
    logging.info(f"Contenuto: {nome_file}")

    sensibilita = data.get("sensibilita", "")
    logging.info(f"Sensibilità: {nome_file}")

    doc_id = data.get("doc_id", "")
    logging.info(f"ID del documento: {nome_file}")

    logging.info(f"[PEP] Richiesta ricevuta da  Ruolo: {role}, Op: {operation}, Documento: {document_type}")

    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
    logging.info(f"client_ip: {client_ip}")

    logging.info("Invio dati al pdp")
    try:
        response = requests.post(PDP_URL, json={
            "timestamp": timestamp,
            "client_ip": client_ip,
            "username": username,
            "role": role,
            "operation": operation,
            "document_type": document_type
        }, timeout=20)
        logging.info(f"Response: {response.json()}")

        pdp_response = response.json()
        decision = pdp_response.get("decision", "deny")
        trust = pdp_response.get("trust", "unknown")
        required = pdp_response.get("required", "unknown")

    except Exception as e:
        logging.info(f"[PEP] Errore nella comunicazione con PDP: {e}")
        decision = "deny"
        trust = "unknown"
        required = "unknown"

    logging.info(f"[PEP] Decisione PDP: {decision} (Trust: {trust}, Soglia: {required})")

    if decision == "allow":
        logging.info("[PEP] Accesso CONCESSO.")
        try:
            if operation == "write":
                success = execute_write_operation(nome_file, contenuto, sensibilita)
                if not success:
                    raise Exception("Fallita scrittura file nel DB")
                result = "Operazione eseguita con successo"
            else:
                result = execute_single_operation(operation, doc_id, role)
                if result is None:
                    return jsonify({
                        "result": "Documento non disponibile per l'operazione richiesta",
                    }), 200

            return jsonify({
                "result": "access granted",
                "response": result
            }), 200

        except Exception as e:
            logging.error(f"[PEP] Errore durante esecuzione operazione: {e}")
            return jsonify({"error": "Errore interno"}), 500
    else:
        logging.info("[PEP] Accesso NEGATO.")
        return jsonify({
            "result": "access denied",
            "trust": trust,
            "required": required
        }), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3100)
