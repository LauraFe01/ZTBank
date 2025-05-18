###
# Obiettivo della policy (Esempio):
# "Permetti l’accesso al DBMS solo ai client che non hanno generato alcun alert Snort nelle ultime 24h."
#  Cosa fa:
# 1) Lo script interroga Splunk ogni minuto per gli IP che hanno generato alert Snort.
# 2) Applica regole iptables per bloccare questi IP dall’accedere al database sulla porta 5432.
# 3) Permette tutti gli altri accessi al DB.
### 

import requests # per fare richieste HTTP (interagire con Splunk REST API).
import subprocess # per eseguire comandi di sistema (qui, iptables)
import time
import json
import urllib3


SPLUNK_HOST = "https://splunk:8089"

# query Splunk che cerca nel database main tutti gli alert di Snort negli ultimi 5 minuti e conta gli IP sorgenti (src_ip)
SPLUNK_SEARCH = 'search index=main sourcetype=snort_alert earliest=-24h | rex field=_raw "\\{[A-Z]+\\}\\s(?<src_ip>\\d{1,3}(?:\\.\\d{1,3}){3}) -> (?<dst_ip>\\d{1,3}(?:\\.\\d{1,3}){3})" | stats count by src_ip'

# IP del DB
DB_IP = "192.168.200.10"
DB_PORT = "5432"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# esegue una query su Splunk per ottenere IP sospetti da bloccare.
# NB: La stringa YWRtaW46TWljb2wwMzAxIQ== è una stringa base64 che ho generato da admin:password da PowerShell:
# [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("admin:vostrapassword"))
def get_blocked_ips():
    # Simula una query a Splunk REST API
    url = f"{SPLUNK_HOST}/services/search/jobs/export"
    headers = {"Authorization": "Basic YWRtaW46TWljb2wwMzAxIQ=="} # stringa da generare da admin:ps
    data = {
        "search": SPLUNK_SEARCH,
        "output_mode": "json"
    }
    r = requests.post(url, headers=headers, data=data, verify=False) # manda la richiesta a splunk
    alerts = []
    for line in r.text.strip().split('\n'): # r.text contiene la risposta in formato JSON, riga per riga 
        entry = json.loads(line)
        if 'src_ip' in entry.get('result', {}):
            alerts.append(entry['result']['src_ip']) # Se la riga contiene un campo src_ip nel risultato, l'IP viene aggiunto alla lista alerts.
    return alerts

# applica la policy firewall per bloccare gli IP sospetti verso il DB.
def apply_firewall_policy(blocked_ips):
    # Verifica se la catena DB_POLICY esiste, altrimenti la crea
    subprocess.run("iptables -w -N DB_POLICY 2>/dev/null || true", shell=True)

    # Pulisce la catena DB_POLICY
    subprocess.run("iptables -w -F DB_POLICY", shell=True)

    # Verifica se la catena è collegata alla catena FORWARD, altrimenti la aggiunge
    check_rule = subprocess.run(
        f"iptables -w -C FORWARD -p tcp --dport {DB_PORT} -j DB_POLICY",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if check_rule.returncode != 0:
        subprocess.run(f"iptables -w -I FORWARD -p tcp --dport {DB_PORT} -j DB_POLICY", shell=True)

    # Blocca gli IP sospetti
    for ip in blocked_ips:
        print(f"Blocco l'accesso al DB per {ip}")
        subprocess.run(f"iptables -w -A DB_POLICY -s {ip} -j DROP", shell=True)

    # Default allow per tutti gli altri
    subprocess.run(f"iptables -w -A DB_POLICY -j ACCEPT", shell=True)


if __name__ == "__main__":
    while True:
        blocked_ips = get_blocked_ips()
        apply_firewall_policy(blocked_ips)
        time.sleep(60)  # aggiorna ogni minuto
