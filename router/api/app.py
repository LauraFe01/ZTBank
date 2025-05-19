from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/enforce', methods=['POST'])
def enforce_policy():
    data = request.get_json()
    ip = data.get("ip")
    action = data.get("action")

    if action == "block" and ip:
        try:
            result = subprocess.run(
                ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                check=True,
                capture_output=True,
                text=True
            )
            return {"status": "blocked", "ip": ip, "output": result.stdout}, 200
        except subprocess.CalledProcessError as e:
            return {"status": "error", "error": e.stderr}, 500
    else:
        return {"error": "Invalid request"}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
