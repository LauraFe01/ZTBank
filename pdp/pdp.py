from flask import Flask, request, jsonify
import requests
import datetime
import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Carica la chiave dal file .env
load_dotenv()
KEY = os.getenv("TRUST_KEY")
if not KEY:
    raise RuntimeError("TRUST_KEY non impostata nell'ambiente")

fernet = Fernet(KEY.encode())
app = Flask(__name__)

TRUST_FILE = "trust_db.json"
trust_db = {}
DEFAULT_TRUST = 100

ROLE_BASE_TRUST = {
    "Direttore": 85,
    "Cassiere": 70,
    "Consulente": 75,
    "Cliente": 60
}

OPERATION_THRESHOLDS = {
    "Dati Personali": {"read": 60, "write": 80},
    "Dati Transazionali": {"read": 65, "write": 75},
    "Documenti Operativi": {"read": 60, "write": 70}
}

# --- Persistenza ---

def load_trust_db():
    global trust_db
    if os.path.exists(TRUST_FILE):
        try:
            with open(TRUST_FILE, "rb") as f:
                encrypted = f.read()
            raw = fernet.decrypt(encrypted)
            trust_db.update(json.loads(raw))
            print("[PDP] trust_db caricato da file cifrato.")
        except Exception as e:
            print(f"[PDP] Errore nella decifratura del trust_db: {e}")
    else:
        print("[PDP] Nessun trust_db.json trovato, uso database vuoto.")

def save_trust_db():
    try:
        raw = json.dumps(trust_db).encode()
        encrypted = fernet.encrypt(raw)
        with open(TRUST_FILE, "wb") as f:
            f.write(encrypted)
        print("[PDP] trust_db salvato su file cifrato.")
    except Exception as e:
        print(f"[PDP] Errore nella cifratura del trust_db: {e}")

# --- Logica trust ---

def adjust_trust(ip, change, reason):
    global trust_db
    now = datetime.datetime.now().isoformat()
    trust = trust_db.get(ip, {"score": DEFAULT_TRUST, "last_seen": now})

    trust["score"] = max(0, min(100, trust["score"] + change))
    trust["last_seen"] = now
    trust["last_reason"] = reason
    trust_db[ip] = trust

    print(f"[PDP] Trust per {ip} aggiornata a {trust['score']} ({reason})")
    save_trust_db()

# --- API ---

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
    client_ip = data.get("client")
    role = data.get("role")
    operation = data.get("operation")  # "read" / "write"
    document_type = data.get("document_type")  # "Dati Personali" etc.

    print(f"[PDP] Valuto {operation.upper()} su {document_type} da {client_ip} (ruolo: {role})")

    # Inizializza se non esiste
    if client_ip not in trust_db:
        base = ROLE_BASE_TRUST.get(role, DEFAULT_TRUST)
        trust_db[client_ip] = {
            "score": base,
            "last_seen": datetime.datetime.now().isoformat(),
            "last_reason": "Ruolo iniziale: " + role
        }
        save_trust_db()

    score = trust_db[client_ip]["score"]
    min_required = OPERATION_THRESHOLDS.get(document_type, {}).get(operation)

    if min_required is None:
        return jsonify({"error": "Operazione o tipo documento non validi"}), 400

    decision = "allow" if score >= min_required else "deny"

    print(f"[PDP] Trust: {score} / Soglia richiesta: {min_required} → Decisione: {decision}")

    return jsonify({
        "decision": decision,
        "trust": score,
        "required": min_required
    }), 200

@app.route("/reward_check", methods=["POST"])
def reward_check():
    now = datetime.datetime.now()
    for ip, data in trust_db.items():
        last_seen = datetime.datetime.fromisoformat(data["last_seen"])
        delta = now - last_seen
        if delta.days >= 60:
            adjust_trust(ip, +5, "No incidents in 60+ days")
    return jsonify({"status": "rewards applied"}), 200

@app.route("/dump", methods=["GET"])
def dump():
    return jsonify(trust_db)

if __name__ == "__main__":
    load_trust_db()
    app.run(host="0.0.0.0", port=5000)