import logging
from flask import jsonify, current_app


logger = logging.getLogger("policy 4")

def handle(data):

    current_app.logger.info(f"[policy 4] Handler chiamato con dati: {data}")
    
    # Aggiungere qui eventuali logiche di policy (richiamando le funzioni che saranno definite negli scripts
    # dentro la cartella utils)

    response = {"status": "policy 4 eseguita", "received_data": data}
    current_app.logger.info(f"[policy 4] Risposta: {response}")
    
    return jsonify(response), 200