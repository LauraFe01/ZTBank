#!/usr/bin/env python3
import sys
import json
import requests
import traceback
from datetime import datetime

LOG_FILE = "/opt/splunk/etc/apps/my_custom_alerts/bin/payload_debug.log"
FLASK_URL = "http://router:5000/enforce"

with open(LOG_FILE, "a") as f:
    f.write(f"{datetime.now().isoformat()} - Script policy_enforcer.py avviato\n")


print("policy_enforcer.py eseguito correttamente")

def log_debug(message):
    """Scrive un messaggio con timestamp nel log file"""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

def main():
    try:
        # Legge lo stdin ricevuto da Splunk
        payload = json.load(sys.stdin)
        log_debug("Payload ricevuto da Splunk:")
        log_debug(json.dumps(payload, indent=2))

        # Estrae l'IP sorgente dalla struttura del payload
        result = payload.get("result", {})
        ip = result.get("src_ip") or result.get("client_ip")

        if not ip:
            log_debug("⚠️ Nessun IP trovato nel payload. Campo 'src_ip' o 'client_ip' mancante.")
            return

        alert_data = {
            "ip": ip,
            "action": "block"
        }

        # Invio al server Flask sul router
        response = requests.post(FLASK_URL, json=alert_data)
        log_debug(f"Invio a Flask: {response.status_code} - {response.text}")

    except Exception as e:
        log_debug("❌ Errore durante l'esecuzione:")
        log_debug(traceback.format_exc())
        print("Errore:", e)

if __name__ == "__main__":
    main()

