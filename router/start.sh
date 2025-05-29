#!/bin/bash
set -e
 
# Avvia rsyslog (ignora errore se già avviato)
service rsyslog start || true
 
# # Gestione robusta PID Squid
# if [ -f /run/squid.pid ]; then
#     PID=$(cat /run/squid.pid)
#     if ! ps -p "$PID" >/dev/null 2>&1; then
#         echo "PID file esistente ma processo non attivo. Lo rimuovo."
#         rm -f /run/squid.pid
#     else
#         echo "Termino istanza precedente di Squid con PID $PID."
#         kill "$PID"
#         sleep 2
#         if ps -p "$PID" >/dev/null 2>&1; then
#             kill -9 "$PID"
#             sleep 1
#         fi
#         rm -f /run/squid.pid
#     fi
# fi
 
# # Pulisce eventuali lock file
# rm -f /var/run/squid.pid || true
 
# # Inizializza cache se necessario
# if [ ! -d /var/spool/squid/00 ]; then
#     echo "Inizializzo cache Squid..."
#     squid -z
# fi
 
# # Assicura permessi log Squid
# mkdir -p /var/log/squid
# chown -R proxy:proxy /var/log/squid
# chmod 755 /var/log/squid
 
# Assicura log Snort
mkdir -p /var/log/snort
chmod 755 /var/log/snort
 
# Assicura log Snort per eth0 ed eth1
mkdir -p /var/log/snort/eth0 /var/log/snort/eth1
chmod 755 /var/log/snort/eth0 /var/log/snort/eth1
 
# Avvia Snort su eth1
echo "Avvio Snort su eth1..."
snort -i eth1 -A fast -c /etc/snort/snort_eth1.conf -l /var/log/snort/eth1 > /var/log/snort/snort_eth1.log 2>&1 &
 
# Avvia Snort su eth0
echo "Avvio Snort su eth0..."
snort -i eth0 -A fast -c /etc/snort/snort_eth0.conf -l /var/log/snort/eth0 > /var/log/snort/snort_eth0.log 2>&1 &
 
# Avvia Snort su eth0
echo "Avvio Snort su eth2..."
snort -i eth2 -A fast -c /etc/snort/snort_eth2.conf -l /var/log/snort/eth2 > /var/log/snort/snort_eth2.log 2>&1 &
 
# Avvia Snort su eth0
echo "Avvio Snort su eth3..."
snort -i eth3 -A fast -c /etc/snort/snort_eth3.conf -l /var/log/snort/eth3 > /var/log/snort/snort_eth3.log 2>&1 &
 
# # Avvia Squid in foreground
# echo "Avvio Squid..."
# squid -NYCd 1 &
 
echo "Setup di SQUID e SNORT completato con successo!"
 
### IPTABLES ###
 
# Nel container router, le interfacce di rete (eth0, eth1, eth2, eth3) corrispondono alle reti Docker:
# - eth0: external-net (192.168.20.0/24)
# - eth1: internal-net (192.168.10.0/24)
# - eth2: net-lab (192.168.200.0/24)
# - eth3: wifi-lan (192.168.30.0/24)
 
 
### IPTABLES ###
 
# Abilita IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.conf.all.forwarding=1
 
# Pulisce regole esistenti
iptables -F
iptables -t nat -F
iptables -t mangle -F
 
# Policy predefinite (cambiate alla fine)
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
 
# Mapping interfacce:
# eth0: external-net (192.168.20.0/24)
# eth1: internal-net (192.168.10.0/24)  
# eth2: net-lab (192.168.200.0/24)
# eth3: wifi-lan (192.168.30.0/24)
 
# Redirezione del traffico HTTP verso Squid (porta 3128)
# iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 3128
# iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 3128
# iptables -t nat -A PREROUTING -i eth3 -p tcp --dport 80 -j REDIRECT --to-port 3128
 
### NAT/MASQUERADING per il traffico in uscita ###
# Permette ai client di comunicare con altre reti attraverso il router
 
# Internal net -> tutte le altre reti
iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o eth0 -j MASQUERADE  # -> external
iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o eth2 -j MASQUERADE  # -> net-lab
iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o eth3 -j MASQUERADE  # -> wifi
 
# External net -> tutte le altre reti  
iptables -t nat -A POSTROUTING -s 192.168.20.0/24 -o eth1 -j MASQUERADE  # -> internal
iptables -t nat -A POSTROUTING -s 192.168.20.0/24 -o eth2 -j MASQUERADE  # -> net-lab
iptables -t nat -A POSTROUTING -s 192.168.20.0/24 -o eth3 -j MASQUERADE  # -> wifi
 
# WiFi net -> tutte le altre reti
iptables -t nat -A POSTROUTING -s 192.168.30.0/24 -o eth0 -j MASQUERADE  # -> external
iptables -t nat -A POSTROUTING -s 192.168.30.0/24 -o eth1 -j MASQUERADE  # -> internal  
iptables -t nat -A POSTROUTING -s 192.168.30.0/24 -o eth2 -j MASQUERADE  # -> net-lab
 
### REGOLE DI FORWARDING ###
 
# Consente il traffico tra le reti tramite il router
# Traffico verso database (PostgreSQL porta 5432)
iptables -A FORWARD -p tcp --dport 5432 -d 192.168.200.10 -j ACCEPT
iptables -A FORWARD -p tcp --sport 5432 -s 192.168.200.10 -j ACCEPT
 
# Traffico generico tra reti (per telnet e altri servizi)
# Internal <-> External
iptables -A FORWARD -s 192.168.10.0/24 -d 192.168.20.0/24 -j ACCEPT
iptables -A FORWARD -s 192.168.20.0/24 -d 192.168.10.0/24 -j ACCEPT
 
# Internal <-> WiFi
iptables -A FORWARD -s 192.168.10.0/24 -d 192.168.30.0/24 -j ACCEPT
iptables -A FORWARD -s 192.168.30.0/24 -d 192.168.10.0/24 -j ACCEPT
 
# External <-> WiFi  
iptables -A FORWARD -s 192.168.20.0/24 -d 192.168.30.0/24 -j ACCEPT
iptables -A FORWARD -s 192.168.30.0/24 -d 192.168.20.0/24 -j ACCEPT
 
# Tutte le reti client <-> net-lab
iptables -A FORWARD -s 192.168.10.0/24 -d 192.168.200.0/24 -j ACCEPT
iptables -A FORWARD -s 192.168.200.0/24 -d 192.168.10.0/24 -j ACCEPT
 
iptables -A FORWARD -s 192.168.20.0/24 -d 192.168.200.0/24 -j ACCEPT
iptables -A FORWARD -s 192.168.200.0/24 -d 192.168.20.0/24 -j ACCEPT
 
iptables -A FORWARD -s 192.168.30.0/24 -d 192.168.200.0/24 -j ACCEPT
iptables -A FORWARD -s 192.168.200.0/24 -d 192.168.30.0/24 -j ACCEPT
 
# Consente traffico loopback e established/related
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
 
# Consenti ping (ICMP)
iptables -A FORWARD -p icmp -j ACCEPT
iptables -A INPUT -p icmp -j ACCEPT
 
# Policy finali (più restrittive)
iptables -P INPUT DROP
iptables -P FORWARD DROP  
iptables -P OUTPUT ACCEPT
 
 
# Avvia l'applicazione Flask
echo "Avvio Flask server..."
python3 /router/api/app.py
 
echo "Setup di FLASK completato con successo!"
 
# Mantiene il container attivo
tail -f /dev/null