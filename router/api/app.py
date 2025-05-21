from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Parametri di connessione al DB
DB_CONFIG = {
    "dbname": "mydb",
    "user": "myuser",
    "password": "mypass",
    "host": "db",  # nome del servizio nel docker-compose
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# NB: Questo file per adesso stampa semplicemente i dati ricevuti attraverso il meccanismo di webhook (serviva come test per
# vedere prima di tutto se i dati arrivavano, in seguito da qui si implementerà la gestione delle policy)

app = Flask(__name__)

# Setup logging su file con rotazione (max 1MB, 3 backup)
log_file = "webhook.log"
if not os.path.exists(log_file):
    open(log_file, 'a').close()

handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route('/splunk-webhook', methods=['POST'])
def splunk_webhook():
    app.logger.info("Webhook endpoint chiamato")
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            # Se payload non è JSON, leggiamo raw text
            raw_data = request.data.decode('utf-8')
            app.logger.info(f"Payload non JSON ricevuto: {raw_data}")
        else:
            app.logger.info(f"Payload JSON ricevuto: {data}")
    except Exception as e:
        app.logger.error(f"Errore durante parsing del payload: {e}")

    return jsonify({"status": "received"}), 200

def verifica_accesso(ruolo, nome_file, sensibilita, azione):
    if ruolo == 'manager':
        return True, "Manager ha accesso completo"
    if ruolo == 'cassiere':
        if sensibilita == 'non_sensibile' and azione == 'lettura':
            return True, "Cassiere puo' leggere file non sensibili"
        return False, "Cassiere non puo' accedere a questo file"
    if ruolo == 'auditor':
        if sensibilita == 'sensibile' and azione == 'lettura' and nome_file.startswith("log_"):
            return True, "Auditor puo' leggere log sensibili"
        return False, "Auditor puo' solo leggere log sensibili"
    return False, "Ruolo non riconosciuto"

@app.route('/splunk-webhook-db', methods=['POST'])
def splunk_webhook_db():
    app.logger.info("Webhook endpoint chiamato")
    try:
        data = request.get_json(force=True, silent=True)
        username = data.get("username")
        file_name = data.get("file_name")
        azione = data.get("azione")

        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Recupera utente e ruolo
        cur.execute("SELECT id, ruolo FROM utenti WHERE username = %s", (username,))
        utente = cur.fetchone()
        if not utente:
            return jsonify({"error": "Utente non trovato"}), 400

        # 2. Recupera file e sensibilità
        cur.execute("SELECT id, sensibilita FROM file_documenti WHERE nome_file = %s", (file_name,))
        file = cur.fetchone()
        if not file:
            return jsonify({"error": "File non trovato"}), 400

        # 3. Verifica accesso
        esito, motivazione = verifica_accesso(utente["ruolo"], file_name, file["sensibilita"], azione)

        # 4. Registra accesso nel log
        cur.execute("""
            INSERT INTO access_log (utente_id, file_id, azione, esito, motivazione)
            VALUES (%s, %s, %s, %s, %s)
        """, (utente["id"], file["id"], azione, esito, motivazione))
        conn.commit()

        return jsonify({"accesso_concesso": esito, "motivazione": motivazione}), 200

    except Exception as e:
        app.logger.error(f"Errore durante parsing del payload: {e}")
        return jsonify({"error": "Errore interno"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
