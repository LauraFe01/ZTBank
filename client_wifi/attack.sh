#!/bin/bash

# IP e porta del PEP sulla rete zt-gateway
PEP_IP="172.24.0.3"
PEP_PORT=3100


# --- Parte 1: richieste HTTP POST simulate ---
for i in {1..3}; do
  echo "Invio richiesta POST"
  curl -s -H "Content-Type: application/json" \
       -d '{"role":"analyst","operation":"read","document_type":"report"}' \
       > /dev/null &
done


echo "Port scanning client_wifi"
echo "Inizio port scanning da 3090 a 3110 verso $PEP_IP"

# Scansione TCP (TCP connect scan) delle porte 3090–3110
nmap -Pn -sS -p3090-3110 $PEP_IP > /dev/null

# Attende la fine dei processi background
wait

echo "Richieste POST inviate."

# --- Parte 2: port scanning TCP delle porte 3070–3120 ---
echo "=== Port scanning da 3070 a 3120 verso $PEP_IP ==="
nmap -Pn -sS -p3070-3120 $PEP_IP > /dev/null

echo "Attacco simulato completato."