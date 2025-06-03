#!/bin/bash

# IP e porta del PEP sulla rete zt-gateway
PEP_IP="172.24.0.3"
PEP_PORT=3100

echo "Simulazione attacco DoS al PEP"


# 20 richieste POST
for i in {1..3}; do
  curl -s -H "Content-Type: application/json" \
       -d '{"role":"analyst","operation":"read","document_type":"report"}' \
       http://$PEP_IP:$PEP_PORT/request > /dev/null &
done

# Attende la fine delle richieste per evitare zombie
wait

echo "Attacco simulato completato."
