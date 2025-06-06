import logging
import ipaddress
import geoip2.database
from utils import adjust_trust


logging.basicConfig(level=logging.INFO)


# Carica il database GeoLite (devi scaricarlo prima)
GEOIP_DB_PATH = 'GeoLite2-Country.mmdb'
geo_reader = geoip2.database.Reader(GEOIP_DB_PATH)


def evaluate_external_net_activity(ip):
    """
    Valuta se l'indirizzo IP appartiene alla rete esterna.
    Se l'IP rientra nella subnet 172.21.0.0/24 (rete esterna),
    riduce il punteggio di fiducia associato di 5 punti.
    """
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.21.0.0/24"):
        adjust_trust(ip, -5, "External net detected")


def evaluate_internal_net_activity(ip):
    """
    Valuta se l'indirizzo IP appartiene alla rete interna.
    Se l'IP rientra nella subnet 172.20.0.0/16 (rete interna),
    aumenta il punteggio di fiducia associato di 10 punti.
    """
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.20.0.0/16"):
        adjust_trust(ip, +10, "Internal net detected")


def evaluate_wifi_net_activity(ip):
    """
    Valuta se l'indirizzo IP appartiene alla rete Wi-Fi.
    Se l'IP rientra nella subnet 172.22.0.0/16 (rete Wi-Fi),
    riduce il punteggio di fiducia associato di 5 punti.
    """
    if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network("172.22.0.0/16"):
        adjust_trust(ip, -5, "Wifi net detected")


def evaluate_ip_country(ip):
    """
    Esegue la geolocalizzazione dell'indirizzo IP.
    Se il paese associato all'IP non è "Italy", riduce il punteggio di fiducia di 40 punti.
    Utilizza il database GeoLite2.
    """
    try:
        response = geo_reader.country(ip)
        country = response.country.name
        logging.info(f"🌍 Accesso da: {country}")
        if country != "Italy":
            adjust_trust(ip, -40, f"Connessione da paese esterno: {country}")
    except Exception as e:
        logging.warning(f"❗ Impossibile geolocalizzare IP {ip}: {e}")


# NB dobbiamo pensare a cosa può fare il ruolo cliente!!!
def evaluate_operation(role, operation):
    """
    Determina se un ruolo ha il permesso di eseguire una determinata operazione.

    - Direttore: accesso completo.
    - Consulente e Cassiere: possono scrivere, ma non cancellare.
    - Altri ruoli o operazioni non esplicitamente gestite: negato.
    """
    if role == "Direttore":
        return True
    if role == "Consulente" or role == "Cassiere":
        if operation == "write":
            return True
        elif operation == "delete":
            return False