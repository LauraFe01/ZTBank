#!/bin/bash

# Avvia rsyslog
service rsyslog start

# Avvia squid
squid -z  # inizializza cache
squid -NYCd 1 &

# Abilita IP forwarding (necessario per NAT/router)
echo 1 > /proc/sys/net/ipv4/ip_forward

# Masquerading per routing verso l'esterno (modifica eth0 se necessario)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Reindirizzamento HTTP (modifica eth1 con interfaccia entrante client)
iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 3128

# Mantieni attivo
tail -f /dev/null
