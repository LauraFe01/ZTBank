import logging
import ipaddress
import geoip2.database
from utils import adjust_trust


logging.basicConfig(level=logging.INFO)


# Carica il database GeoLite (devi scaricarlo prima)
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
geo_reader = geoip2.database.Reader(GEOIP_DB_PATH)


# toglie 5 punti di fiducia nel caso di richieste proveniente da reti esterne
def evaluate_external_net_activity(ip):
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.21.0.0/24"):
        adjust_trust(ip, -5, "External net detected")

# aggiunge 10 punti di fiducia nel caso di richieste provenienti da reti interne
def evaluate_internal_net_activity(ip):
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.20.0.0/16"):
        adjust_trust(ip, +10, "Internal net detected")

# aggiunge 5 punti di fiducia nel caso di richieste provenienti da reti wifi
def evaluate_wifi_net_activity(ip):
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.22.0.0/16"):
        adjust_trust(ip, -5, "Wifi net detected")


# toglie 40 punti di fiducia nel caso di richieste provenienti dall'estero
def evaluate_ip_country(trust_key):
    ip = trust_key.split("|")[1]
    # Geolocalizzazione IP
    try:
        response = geo_reader.country(ip)
        country = response.country.name
        logging.info(f"🌍 Accesso da: {country}")
        if country != "Italy":
            adjust_trust(trust_key, -40, f"Connessione da paese esterno: {country}")
    except Exception as e:
        logging.warning(f"❗ Impossibile geolocalizzare IP {ip}: {e}")

# NB dobbiamo pensare a cosa può fare il ruolo cliente!!!
def evaluate_operation(role, operation):
    if role == "Direttore":
        return True
    if role == "Consulente" or role == "Cassiere":
        if operation == "write":
            return True
        elif operation == "delete":
            return False