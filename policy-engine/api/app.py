from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
