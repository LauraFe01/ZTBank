from flask import Flask, request, jsonify
import requests
import psycopg2
import logging

app = Flask(__name__)

# rotta attraverso la quale il PEP invia i dati al PDP per la valutazione diretta della fiducia
PDP_URL = "http://pdp:5050/decide"

logging.basicConfig(level=logging.INFO)

# rotta attraverso la quale il PEP riceve la richiesta dal client(gateway)
@app.route("/request", methods=["POST"])
def handle_request():
    data = request.get_json()

    #client_id = data.get("client", "")
    role = data.get("role", "")
    operation = data.get("operation", "")
    document_type = data.get("document_type", "")

    logging.info(f"[PEP] Richiesta ricevuta da  Ruolo: {role}, Op: {operation}, Documento: {document_type}")
    if request.headers.getlist("X-Forwarded-For"):
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
    logging.info(f"client_ip: {client_ip}")

    # Inoltra tutto al PDP
    try:
        response = requests.post(PDP_URL, json={
            "client_ip": client_ip,
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
        logging.info("[PEP] Accesso CONCESSO (simulazione DB).")
        return jsonify({
            "result": "access granted",
            "trust": trust,
            "required": required
        }), 200
    else:
        logging.info("[PEP] Accesso NEGATO.")
        return jsonify({
            "result": "access denied",
            "trust": trust,
            "required": required
        }), 403


@app.route("/get_data", methods=["GET"]) # dobbiamo modificarlo con il tipo di richiesta che ci serve
def get_data():
    try:
        conn = psycopg2.connect(
            host="172.25.0.4",  # IP del container db (zt-core)
            dbname="bankDB",
            user="user",
            password="cyber_pwd"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM file_documenti")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3100)
