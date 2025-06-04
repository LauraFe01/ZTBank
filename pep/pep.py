import os
from user_auth import load_user_db, authenticate_user
from flask import Flask, request, jsonify, session
import requests
import psycopg2
import logging
import pytz
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("PEP_SECRET_KEY")
PDP_URL = "http://pdp:5050/decide"
logging.basicConfig(level=logging.INFO)

rome = pytz.timezone("Europe/Rome")

@app.route("/login", methods=["POST"])
def login():
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
    session.clear()
    return jsonify({"status": "ok", "message": "Logout effettuato"}), 200

@app.route("/request", methods=["POST"])
def handle_request():
    if "username" not in session or "role" not in session:
        return jsonify({"error": "Utente non autenticato"}), 401

    role = session["role"]
    username = session["username"]

    data = request.get_json()

    timestamp = datetime.now(rome).strftime("%Y-%m-%d %H:%M:%S")

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
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode='require'
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