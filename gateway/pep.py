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
        response = requests.post(PDP_URL, json={"client": client_id}, timeout=2)
        decision = response.json().get("decision", "deny")
    except Exception as e:
        print(f"[PEP] Errore nella comunicazione con PDP: {e}")
        decision = "deny"

    print(f"[PEP] Decisione PDP: {decision}")

    if decision == "allow":
        # 🔒 Simulazione accesso al DB (in futuro sostituire con query reale)
        print("[PEP] (Simulazione) Connessione al DB CONCESSA.")
        return jsonify({"result": "access granted"}), 200
    else:
        print("[PEP] Accesso al DB NEGATO.")
        return jsonify({"result": "access denied"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)