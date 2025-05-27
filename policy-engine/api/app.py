# qui in questo file le richieste che provengono dal meccanismo webhook vengono filtrate in base al nome della saved search da cui
# provengono, in modo da implementare il meccanismo di gestione nel modulo corretto, per quella policy specifica

from flask import Flask, request, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os

# Import dei moduli di gestione delle policy
# Dentro ogni file c’è una funzione handle(data) che gestisce il payload relativo a quella policy.
from policies import policy_1, policy_2, policy_3, policy_4

# Crea l’istanza dell’app Flask
app = Flask(__name__)

# Setup logging su file con rotazione (max 1MB, 3 backup)
log_file = "webhook.log"
if not os.path.exists(log_file):
    open(log_file, 'a').close()

# Crea un gestore di log che scrive sul file webhook.log.
handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Mappa policy_id → funzione handler
# Definisce un dizionario che associa il nome di una saved search a una funzione handler corrispondente.
# Serve per smistare dinamicamente le chiamate al metodo giusto 
POLICY_MAP = {
    "TrustScoreReduction_AttackAttempts": policy_1.handle,
    "savedsearch_name_2": policy_2.handle,
    "savedsearch_name_3": policy_3.handle,
    "savedsearch_name_4": policy_4.handle
}

# Definisce un endpoint HTTP /splunk-webhook che accetta solo richieste POST.
# La funzione webhook() sarà chiamata ogni volta che arriva una POST su /splunk-webhook.
@app.route('/splunk-webhook', methods=['POST'])
def webhook():
    app.logger.info("Webhook endpoint chiamato")
    try:
        data = request.get_json(force=True, silent=True)
        if data is None:
            raw_data = request.data.decode('utf-8')
            app.logger.info(f"Payload non JSON ricevuto: {raw_data}")
            return jsonify({"error": "Payload non JSON"}), 400

        app.logger.info(f"Payload JSON ricevuto: {data}")
        
        # qui si estrae il nome della saved search per smistare la chiamata al giusto modulo di gestione
        search_name = data.get("search_name")
        if not search_name:
            app.logger.warning("Manca 'search_name' nel payload")
            return jsonify({"error": "Missing search name"}), 400

        handler = POLICY_MAP.get(search_name)
        if handler:
            # Invoca il gestore specifico per la policy
            response = handler(data)
            return response
        else:
            app.logger.warning(f"search_name sconosciuto: {search_name}")
            return jsonify({"error": "Unknown search_name"}), 400

    except Exception as e:
        app.logger.error(f"Errore durante parsing del payload o esecuzione handler: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
