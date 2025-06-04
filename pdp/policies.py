import logging
import ipaddress
import geoip2.database
from utils import adjust_trust

logging.basicConfig(level=logging.INFO)

# Carica il database GeoLite (devi scaricarlo prima)
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
geo_reader = geoip2.database.Reader(GEOIP_DB_PATH)

# toglie 10 punti di fiducia nel caso di richieste proveniente da reti esterne
def evaluate_external_net_activity(ip):
    if ipaddress.IPv4Address(ip) not in ipaddress.IPv4Network("172.20.0.0/24"):
        adjust_trust(ip, -20, "External net detected")

# aggiunge 10 punti di fiducia nel caso di richieste provenienti da reti interne
def evaluate_internal_net_activity(ip):
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.20.0.0/16"):
        adjust_trust(ip, +10, "Internal net access")

# aggiunge 10 punti di fiducia nel caso di richieste provenienti dall'estero
def evaluate_ip_country(ip):

    # Geolocalizzazione IP
    try:
        response = geo_reader.country(ip)
        country = response.country.name
        logging.info(f"🌍 Accesso da: {country}")
        if country != "Italy":
            adjust_trust(ip, -40, f"Connessione da paese esterno: {country}")
    except Exception as e:
        logging.warning(f"❗ Impossibile geolocalizzare IP {ip}: {e}")