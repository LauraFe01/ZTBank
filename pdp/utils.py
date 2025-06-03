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