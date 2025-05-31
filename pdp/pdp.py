from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/decide", methods=["POST"])
def decide():
    data = request.json
    client = data.get("client", "")
    print(f"[PDP] Valuto richiesta dal client: {client}")
    
    # Regola: blocca solo external_client
    #placeholder
    if client == "external_client":
        return jsonify({"decision": "deny"})
    return jsonify({"decision": "allow"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
