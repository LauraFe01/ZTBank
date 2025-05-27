#!/bin/bash
set -e

# Avvia rsyslog (ignora errore se già avviato)
service rsyslog start || true

# Abilita IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Reset iptables
iptables -t nat -F POSTROUTING
iptables -t nat -F PREROUTING

# Regole iptables iniziali
iptables -A FORWARD -p tcp --dport 5432 -j DROP
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth2 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth3 -p tcp --dport 80 -j REDIRECT --to-port 3128
# Permetti traffico SSH da client-external (192.168.20.0/24) verso client-internal (192.168.10.10)
iptables -I FORWARD -s 192.168.20.0/24 -d 192.168.10.10 -p tcp --dport 22 -j ACCEPT

# Avvia l'applicazione Flask
echo "Avvio Flask server..."
python3 /policy-engine/api/app.py 

echo "Setup completato con successo!"


