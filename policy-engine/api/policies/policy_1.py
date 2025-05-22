import logging
from flask import jsonify, current_app

logger = logging.getLogger("policy 1")

def handle(data):

    current_app.logger.info(f"[policy 1] Handler chiamato con dati: {data}")
    
    # Aggiungere qui eventuali logiche di policy (richiamando le funzioni che saranno definite negli scripts
    # dentro la cartella utils)

    response = {"status": "policy 1 eseguita", "received_data": data}
    current_app.logger.info(f"[policy 1] Risposta: {response}")
    
    return jsonify(response), 200