from flask import Flask, request, jsonify
import requests
import datetime

app = Flask(__name__)

# In-memory storage (puoi persistere con un file o DB se serve)
trust_db = {}

DEFAULT_TRUST = 100

def adjust_trust(ip, change, reason):
    global trust_db
    now = datetime.datetime.now()
    trust = trust_db.get(ip, {"score": DEFAULT_TRUST, "last_seen": now})
    
    trust["score"] = max(0, min(100, trust["score"] + change))  # Clamp between 0-100
    trust["last_seen"] = now
    trust["last_reason"] = reason
    trust_db[ip] = trust
    print(f"[PDP] Trust per {ip} aggiornata a {trust['score']} ({reason})")

@app.route("/update_trust", methods=["POST"])
def update_trust():
    data = request.json
    trust_type = data.get("type")

    if trust_type == "blacklist":
        ips = data.get("ips", "").split()
        for ip in ips:
            adjust_trust(ip, -30, "Blacklist match")

    elif trust_type == "attack":
        ip = data.get("src_ip")
        count = int(data.get("count", 0))
        if count > 10:
            adjust_trust(ip, -30, f"{count} attacks detected")

    elif trust_type == "anomaly":
        ip = data.get("src_ip")
        count = int(data.get("count", 0))
        if count > 30:
            adjust_trust(ip, -20, f"{count} anomalous accesses")

    return jsonify({"status": "trust updated"}), 200

@app.route("/decide", methods=["POST"])
def decide():
    data = request.json
    client_ip = data.get("client", "")
    print(f"[PDP] Valuto richiesta dal client: {client_ip}")

    trust = trust_db.get(client_ip, {"score": DEFAULT_TRUST})["score"]

    # Aggiunta della regola: se fiducia < 60 nega
    if trust < 60:
        decision = "deny"
    else:
        decision = "allow"

    print(f"[PDP] Decisione per {client_ip}: {decision} (Trust: {trust})")

    # Invia al PEP (opzionale, se vuoi inoltrare attivamente)
    # requests.post("http://pep:3100/decision_update", json={"client": client_ip, "decision": decision})

    return jsonify({"decision": decision, "trust": trust})

# Cron job-like reward
@app.route("/reward_check", methods=["POST"])
def reward_check():
    now = datetime.datetime.now()
    for ip, data in trust_db.items():
        delta = now - data["last_seen"]
        if delta.days >= 60:
            adjust_trust(ip, +5, "No incidents in 60+ days")
    return jsonify({"status": "rewards applied"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
