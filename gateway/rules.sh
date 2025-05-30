#!/bin/bash

# Attiva log più dettagliato (opzionale)
echo "[Gateway] Avvio iptables..."

# Flush delle regole precedenti
iptables -F
iptables -X

# Default: blocca tutto
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT


# Logga tutto in INPUT
iptables -A INPUT -j LOG --log-level info

# Logga tutto in OUTPUT
iptables -A OUTPUT -j LOG --log-prefix "[IPTABLES OUTPUT] " --log-level 4

# Logga tutto in FORWARD (se instradi tra reti)
iptables -A FORWARD -j LOG --log-prefix "[IPTABLES FORWARD] " --log-level 4


# Permetti localhost
iptables -A INPUT -i lo -j ACCEPT

# Permetti connessioni già stabilite
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Ottieni IP dei client (risolti via Docker DNS)
INT_IP=$(getent hosts internal_client | awk '{ print $1 }')
EXT_IP=$(getent hosts external_client | awk '{ print $1 }')

# Permetti solo internal_client
iptables -A INPUT -s "$INT_IP" -j ACCEPT

# Avvia rsyslog
echo "[INFO] Avvio rsyslogd..."
rsyslogd

# Mostra regole attive
echo "[INFO] Regole attive:"
iptables -L -n

# Mantieni il container vivo e mostra log
echo "[INFO] In ascolto su /var/logs/iptables.log..."
touch /var/logs/iptables.log
chmod 666 /var/logs/iptables.log
tail -f /var/logs/iptables.log