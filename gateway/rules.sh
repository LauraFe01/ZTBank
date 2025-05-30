#!/bin/bash

echo "[Gateway] Avvio iptables..."

# Flush delle regole precedenti
iptables -F
iptables -X

# Policy predefinite
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Permetti localhost
iptables -A INPUT -i lo -j ACCEPT

# Permetti connessioni già stabilite
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Attesa attiva finché il DNS Docker risolve correttamente
echo "[Gateway] Attendo che internal_client sia raggiungibile..."
while true; do
  INT_IP=$(getent hosts internal_client | awk '{ print $1 }')
  if [[ -n "$INT_IP" ]]; then break; fi
  sleep 1
done
echo "[Gateway] IP di internal_client: $INT_IP"

echo "[Gateway] Attendo che external_client sia raggiungibile..."
while true; do
  EXT_IP=$(getent hosts external_client | awk '{ print $1 }')
  if [[ -n "$EXT_IP" ]]; then break; fi
  sleep 1
done
echo "[Gateway] IP di external_client: $EXT_IP"

# Rimuove eventuali zeri iniziali (es. 172.18.0.04 → 172.18.0.4)
INT_IP=$(echo "$INT_IP" | sed 's/\b0\+\([0-9]\)/\1/g')
EXT_IP=$(echo "$EXT_IP" | sed 's/\b0\+\([0-9]\)/\1/g')

# Permetti solo internal_client
iptables -A INPUT -s "$INT_IP" -j ACCEPT

# Mostra le regole attive
echo "[INFO] Regole attive:"
iptables -L -n

# Mantieni il container attivo
tail -f /dev/null
