#!/bin/bash

# Attendi che il gateway sia raggiungibile
GATEWAY_IP="192.168.10.254"  # Modifica per ogni client
MAX_ATTEMPTS=50
ATTEMPT=0

echo "[INFO] Attendo che il gateway $GATEWAY_IP sia raggiungibile..."
while ! ping -c 1 -W 1 $GATEWAY_IP > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "[ERROR] Gateway non raggiungibile dopo $MAX_ATTEMPTS tentativi"
        exit 1
    fi
    echo "[INFO] Tentativo $ATTEMPT/$MAX_ATTEMPTS - Gateway non ancora pronto..."
    sleep 2
done

echo "[INFO] Gateway raggiungibile, configuro la route..."
ip route del default 2>/dev/null
ip route add default via $GATEWAY_IP


echo "[INFO] Accesso legittimo al DB..."
PGPASSWORD="mypass" psql -h 192.168.200.10 -U myuser -d mydb -c "SELECT NOW();" >/dev/null 2>&1

echo "[INFO] Simulazione attacco SQL Injection..."
echo "' OR '1'='1'; --" | nc 192.168.200.10 5432 >/dev/null 2>&1

echo "[INFO] Altro traffico generico (ping + curl)..."
ping -c 2 192.168.200.10 >/dev/null 2>&1
curl -s http://192.168.200.10 >/dev/null 2>&1 || true

echo "[INFO] Script completato, avvio bash interattiva"
exec "$@"
