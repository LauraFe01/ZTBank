#!/usr/bin/env python3
import sys
import json
import requests
import traceback
from datetime import datetime

LOG_FILE = "/opt/splunk/etc/apps/my_custom_alerts/bin/payload_debug.log"
FLASK_URL = "http://192.168.200.254:5000/enforce"

with open(LOG_FILE, "a") as f:
    f.write(f"{datetime.now().isoformat()} - Script policy_enforcer.py avviato\n")


print("policy_enforcer.py eseguito correttamente")

def log_debug(message):
    """Scrive un messaggio con timestamp nel log file"""
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")

def main():
    try:
        if sys.stdin.isatty():
            log_debug("❗ Nessun input ricevuto da Splunk (stdin è vuoto)")
            return

        payload_str = sys.stdin.read().strip()
        log_debug(f"📥 Payload grezzo da stdin:\n{payload_str!r}")

        if not payload_str:
            log_debug("❗ Stdin è vuoto: nessun payload JSON ricevuto.")
            return

        try:
            payload = json.loads(payload_str)
            log_debug("✅ Payload JSON ricevuto e parsato:")
            log_debug(json.dumps(payload, indent=2))
        except json.JSONDecodeError as e:
            log_debug(f"❌ Errore di parsing JSON: {e}")
            return

        result = payload.get("result", {})
        ip = result.get("src_ip") or result.get("client_ip")

        if not ip:
            log_debug("⚠️ Nessun IP trovato nel payload. Campo 'src_ip' o 'client_ip' mancante.")
            return

        alert_data = {
            "ip": ip,
            "action": "block"
        }

        try:
            response = requests.post(FLASK_URL, json=alert_data)
            try:
                json_response = response.json()
                log_debug(f"✅ Risposta JSON da Flask: {json.dumps(json_response, indent=2)}")
            except ValueError:
                log_debug(f"⚠️ Risposta non-JSON da Flask: {response.text}")
        except Exception as req_err:
            log_debug("❌ Errore durante l'invio della richiesta POST:")
            log_debug(str(req_err))

    except Exception as e:
        log_debug("❌ Errore generale durante l'esecuzione:")
        log_debug(traceback.format_exc())

if __name__ == "__main__":
    main()

