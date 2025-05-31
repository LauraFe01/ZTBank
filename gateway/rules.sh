#!/bin/bash

echo "[Gateway] Configurazione iptables..."

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

# Permetti accesso alla porta 3128 solo da internal_client
iptables -A INPUT -p tcp --dport 3128 -s 172.18.0.5 -j ACCEPT
iptables -A INPUT -p tcp --dport 3128 -j DROP

# Permetti al PEP di accedere al DB
iptables -A FORWARD -s 172.18.0.3 -d 172.18.0.7 -p tcp --dport 5432 -j ACCEPT
iptables -A FORWARD -p tcp --dport 5432 -j DROP

echo "[Gateway] Regole iptables configurate."
