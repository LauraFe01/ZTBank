import time
import requests

PDP_URL = "http://pdp:5000/decide"

def simulate_request(client_id):
    print(f"[PEP] Ricevuta richiesta dal client: {client_id}")
    response = requests.post(PDP_URL, json={"client": client_id})
    decision = response.json().get("decision", "deny")
    print(f"[PEP] Decisione PDP: {decision}")
    if decision == "allow":
        #ACCESSO REALE AL DB
        print("[PEP] Accesso al DB CONCESSO.")
    else:
        print("[PEP] Accesso al DB NEGATO.")

if __name__ == "__main__":
    while True:
        simulate_request("wifi_client")
        time.sleep(10)
