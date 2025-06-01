from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
PDP_URL = "http://pdp:5000/decide"

@app.route("/request", methods=["POST"])
def handle_request():
    data = request.get_json()
    client_id = data.get("client", "")
    print(f"[PEP] Ricevuta richiesta dal client: {client_id}")

    try:
        # Inoltra al PDP il client ID
        response = requests.post(PDP_URL, json={"client": client_id}, timeout=2)
        pdp_response = response.json()
        decision = pdp_response.get("decision", "deny")
        trust = pdp_response.get("trust", "unknown")
    except Exception as e:
        print(f"[PEP] Errore nella comunicazione con PDP: {e}")
        decision = "deny"
        trust = "unknown"

    print(f"[PEP] Decisione PDP: {decision} (Trust: {trust})")

    if decision == "allow":
        # 🔒 Simulazione accesso al DB (in futuro sostituire con query reale)
        print("[PEP] (Simulazione) Connessione al DB CONCESSA.")
        return jsonify({
            "result": "access granted",
            "client": client_id,
            "trust": trust
        }), 200
    else:
        print("[PEP] Accesso al DB NEGATO.")
        return jsonify({
            "result": "access denied",
            "client": client_id,
            "trust": trust
        }), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3100)
