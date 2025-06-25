import logging
import ipaddress
import geoip2.database
from utils import adjust_trust


logging.basicConfig(level=logging.INFO)


# Carica il database GeoLite (va prima scaricato)
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


def evaluate_operation(role, operation):
    """
    Determina se un ruolo ha il permesso di eseguire una determinata operazione.

    - Direttore: accesso completo.
    - Consulente e Cassiere: possono scrivere, ma non cancellare.
    - Altri ruoli o operazioni non esplicitamente gestite: negato.
    """
    if role == "Direttore":
        return True
    elif role == "Consulente" or role == "Cassiere":
        if operation == "write":
            return True
        elif operation == "delete":
            return False
        

def evaluate_data(role, document_type):
    """
    Determina se un ruolo ha il permesso di accedere alla risorsa del db richiesta.
    
    - Direttore: accesso a tutti i tipi di documenti
    - Cassiere: può accedere a dati transazionali e documenti operativi
    - Consulente: può accedere a documenti operativi
    - Cliente: può accedere a dati personali (i propri ma non specifichiamo)
    """
    if role == "Direttore":
        return True
    elif role == "Cassiere":
        if document_type == "Dati Transazionali" or document_type == "Documenti Operativi":
            return True
    elif role == "Consulente":
        if document_type == "Documenti Operativi":
            return True
    elif role == "Cliente":
        if document_type == "Dati Personali":
            return True
    else:
        return False