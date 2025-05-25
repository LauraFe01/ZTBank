import logging
from flask import jsonify, current_app

logger = logging.getLogger("policy 2")

def handle(data):
    
    current_app.logger.info(f"[policy 2] Handler chiamato con dati: {data}")
    
    # Aggiungere qui eventuali logiche di policy (richiamando le funzioni che saranno definite negli scripts
    # dentro la cartella utils)

    response = {"status": "policy 2 eseguita", "received_data": data}
    current_app.logger.info(f"[policy 2] Risposta: {response}")
    
    return jsonify(response), 200