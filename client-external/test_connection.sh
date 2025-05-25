#!/bin/bash
# Script per testare le connessioni dal client-external

echo "=== Test di connettività dal client-external ==="
echo ""

# Test 1: Ping verso policy-engine (router)
echo "1. Test ping verso policy-engine (router):"
ping -c 3 192.168.20.254
echo ""

# Test 2: Ping verso database
echo "2. Test ping verso database:"
ping -c 3 192.168.200.10
echo ""

# Test 3: Ping verso client-internal
echo "3. Test ping verso client-internal:"
ping -c 3 192.168.10.10
echo ""

# Test 4: Ping verso network-monitor
echo "4. Test ping verso network-monitor:"
ping -c 3 192.168.200.253
echo ""

# Test 5: Test connessione HTTP verso policy-engine API
echo "5. Test HTTP verso policy-engine API:"
curl -m 10 http://192.168.20.254:5000/ 2>/dev/null || echo "Connessione HTTP fallita"
echo ""

# Test 6: Test connessione PostgreSQL (se psql è disponibile)
echo "6. Test connessione PostgreSQL:"
if command -v nc &> /dev/null; then
    echo "Test porta 5432 del database:"
    nc -zv 192.168.200.10 5432 2>&1
else
    echo "netcat non disponibile, installo..."
    apt-get update -qq && apt-get install -y netcat -qq
    echo "Test porta 5432 del database:"
    nc -zv 192.168.200.10 5432 2>&1
fi
echo ""

# Test 7: Traceroute per verificare il path di routing
echo "7. Traceroute verso database:"
if command -v traceroute &> /dev/null; then
    traceroute 192.168.200.10
else
    echo "traceroute non disponibile, uso ping con TTL crescente"
    for i in {1..3}; do
        echo "TTL $i:"
        ping -c 1 -t $i 192.168.200.10 2>&1 | grep "Time to live exceeded" || true
    done
fi
echo ""

# Mostra tabella di routing finale
echo "=== Tabella di routing corrente ==="
ip route show
echo ""

echo "Test completati!"