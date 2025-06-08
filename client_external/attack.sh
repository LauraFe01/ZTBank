#!/bin/bash

# IP e porta del PEP sulla rete zt-gateway
PEP_IP="172.24.0.3"
PEP_PORT=3100

# echo "=== Simulazione attacco DoS autenticato al PEP ==="

# --- Parte 1: invio delle richieste HTTP POST (DoS simulato) ---
for i in {1..3}; do
  echo "[$i] Invio richiesta POST autenticata a /request"
  curl -s -X POST http://$PEP_IP:$PEP_PORT/request \
       -H "Content-Type: application/json" \
       -d '{"role":"analyst","operation":"read","document_type":"report"}' \
       #> /dev/null &
done

# Attende che finiscano i processi in background
wait
echo "Richieste POST inviate."

# --- Parte 2: port scanning TCP delle porte 3070–3120 ---
echo "=== Port scanning da 3070 a 3120 verso $PEP_IP ==="
nmap -Pn -sS -p3070-3120 $PEP_IP
echo "Port scanning completato."

# --- Parte 3: invio payload MIPS SGI NOOP per test Snort ---
echo "=== Invio payload SGI NOOP sled per triggerare la regola Snort ==="
echo -ne $'\x03\xe0\xf8%\x03\xe0\xf8%\x03\xe0\xf8%\x03\xe0\xf8%' | nc -u -w1 172.24.0.3 3100

echo "Payload inviato!"
