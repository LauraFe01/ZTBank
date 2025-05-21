import requests
import xml.etree.ElementTree as ET
import json

# === CONFIGURA QUI ===
splunk_host = "https://192.168.200.5:8089"
username = "admin"
password = "Chang3dP@ss!"
index = "main"
sourcetype = "snort_alert"
src_ip = "192.168.1.123"  # IP da bloccare nel test
savedsearch_name = "BlockIPAlert1"  # Forza questa search

# === LOGIN SPLUNK (porta 8089) ===
def get_session_key():
    auth_url = f"{splunk_host}/services/auth/login"
    response = requests.post(auth_url, data={"username": username, "password": password}, verify=False)
    if response.status_code != 200:
        raise Exception(f"Login fallito: {response.text}")
    root = ET.fromstring(response.text)
    return root.findtext("sessionKey")

# === INVIO EVENTO ===
def send_test_event(session_key):
    url = f"{splunk_host}/services/receivers/simple"
    headers = {
        "Authorization": f"Splunk {session_key}"
    }
    payload = f'src_ip={src_ip} msg="ICMP Ping detected"'
    params = {
        "index": index,
        "sourcetype": sourcetype
    }
    response = requests.post(url, headers=headers, params=params, data=payload, verify=False)
    print(f"[EVENTO] Status: {response.status_code} - {response.text}")

# === FORZA LA SEARCH ===
def trigger_saved_search(session_key):
    url = f"{splunk_host}/servicesNS/admin/search/saved/searches/{savedsearch_name}/dispatch"
    headers = {
        "Authorization": f"Splunk {session_key}"
    }
    data = {
        "trigger_actions": "1"
    }
    response = requests.post(url, headers=headers, data=data, verify=False)
    print(f"[DISPATCH] Status: {response.status_code} - {response.text}")

# === MAIN ===
if __name__ == "__main__":
    try:
        print("[*] Autenticazione a Splunk...")
        session_key = get_session_key()
        print("[✓] Login OK")

        print("[*] Invio evento test...")
        send_test_event(session_key)

        print("[*] Attivazione savedsearch (facoltativo)...")
        trigger_saved_search(session_key)

        print("[✓] Test completato. Controlla il log payload_debug.log.")
    except Exception as e:
        print(f"[ERRORE] {e}")
