import os
from user_auth import load_user_db, authenticate_user
from flask import Flask, request, jsonify, session
import requests
import psycopg2
import logging
import pytz
from datetime import datetime
from db_scripts.db_exec import execute_single_operation, execute_write_operation



app = Flask(__name__) # # Inizializzazione dell'app Flask
app.secret_key = os.getenv("PEP_SECRET_KEY") # Chiave segreta per gestire le sessioni utente
PDP_URL = "http://pdp:5050/decide" # Endpoint del PDP (Policy Decision Point)
logging.basicConfig(level=logging.INFO) # Configurazione logging
rome = pytz.timezone("Europe/Rome") # Timezone locale



# Endpoint per il login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # autentichiamo l'utente e se l'operazione non va a buon fine inviamo un messaggio di errore
    user_db = load_user_db() 
    success, role_or_msg = authenticate_user(username, password, user_db)
    if not success:
        return jsonify({"status": "error", "message": role_or_msg}), 401
    
    # se l'autenticazione va a buon fine, avviamo la sessione per l'utente
    session.permanent = True # Sessione persistente
    session["username"] = username
    session["role"] = role_or_msg
    return jsonify({"status": "ok", "message": "Login riuscito"}), 200



# Endpoint per il logout
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "ok", "message": "Logout effettuato"}), 200



# rotta di ricezione delle richieste
@app.route("/request", methods=["POST"])
def handle_request():
    logging.info("Richiesta ricevuta all'endpoint /request")
    logging.info(f"Headers: {request.headers}")
    logging.info(f"Corpo della richiesta: {request.get_data()}")
    data = request.get_json()
    logging.info(f"Dati JSON ricevuti: {data}")

    # Verifica autenticazione (solo gli autenticati possono fare richieste)
    if "username" not in session or "role" not in session:
        return jsonify({"error": "Utente non autenticato"}), 401

    role = session["role"]
    logging.info(f"Ruolo dell'utente: {role}")

    username = session["username"]
    logging.info(f"Username dell'utente: {username}")

    timestamp = datetime.now(rome).strftime("%Y-%m-%d %H:%M:%S")
    
    # estrazione dei parametri della richiesta (la sensibilità la mettiamo nella richiesta?????)
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

    # Ottieniamo IP del client
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
    logging.info(f"client_ip: {client_ip}")

    # Inoltriamo tutto al PDP
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
    
    # Se l'accesso è consentito, esegui l'operazione
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
        # Accesso negato 
        logging.info("[PEP] Accesso NEGATO.")
        return jsonify({
            "result": "access denied",
            "trust": trust,
            "required": required

        }), 403



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3100)