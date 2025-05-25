#!/bin/bash
# Script per configurare le rotte nel client-external

echo "Configurazione rotte per client-external..."

# Mostra configurazione attuale
echo "=== Configurazione di rete attuale ==="
ip route show
echo ""

# Rimuovi eventuale default route esistente (opzionale)
# ip route del default 2>/dev/null || true

# Aggiungi rotta verso la rete net-lab (dove si trova il DB) tramite policy-engine
echo "Aggiunta rotta verso net-lab (192.168.200.0/24) via policy-engine..."
ip route add 192.168.200.0/24 via 192.168.20.254 dev eth0

# Aggiungi rotta verso internal-net tramite policy-engine  
echo "Aggiunta rotta verso internal-net (192.168.10.0/24) via policy-engine..."
ip route add 192.168.10.0/24 via 192.168.20.254 dev eth0

# Aggiungi rotta verso wifi-lan tramite policy-engine
echo "Aggiunta rotta verso wifi-lan (192.168.30.0/24) via policy-engine..."
ip route add 192.168.30.0/24 via 192.168.20.254 dev eth0

# Imposta policy-engine come default gateway
echo "Impostazione policy-engine come default gateway..."
ip route add default via 192.168.20.254 dev eth0

echo "=== Nuova configurazione di rete ==="
ip route show
echo ""

echo "=== Test di connettività ==="
echo "Test ping verso policy-engine (192.168.20.254):"
ping -c 3 192.168.20.254

echo ""
echo "Test ping verso database (192.168.200.10):"
ping -c 3 192.168.200.10

echo "Configurazione rotte completata!"