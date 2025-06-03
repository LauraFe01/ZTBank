import os
import subprocess
import logging 

BLACKLIST_FILE = "/app/blacklist/blacklist.txt"

def block_ip(ip):
    try:
        with open(BLACKLIST_FILE, "a") as f:
            f.write(f"{ip}\n")
        logging.warning(f"[PDP] IP {ip} aggiunto alla blacklist condivisa.")
    except Exception as e:
        logging.error(f"[PDP] Errore scrittura blacklist: {e}")

def check_blacklist_file(ip):
    logging.info(f"[PDP] Controllo blacklist per l'IP: {ip}")
    blacklist_path = "data/blacklist/blacklist.txt"
    if not os.path.exists(blacklist_path):
        logging.warning("Blacklist file non trovato.")
        return False
    with open(blacklist_path, "r") as f:
        blacklisted_ips = set(line.strip() for line in f if line.strip())
    return ip in blacklisted_ips
