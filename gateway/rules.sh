#!/bin/bash

echo "[Gateway] Configurazione iptables..."

# 1️⃣ Abilita l'inoltro IP (fondamentale per il NAT)
echo 1 > /proc/sys/net/ipv4/ip_forward

# 2️⃣ Flush delle regole precedenti
iptables -F
iptables -X
iptables -t nat -F

# 3️⃣ Policy predefinite
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 4️⃣ Permetti localhost
iptables -A INPUT -i lo -j ACCEPT

# 5️⃣ Permetti connessioni già stabilite
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# 6️⃣ Permetti accesso a Squid (porta 3128) solo dai client
iptables -A INPUT -p tcp --dport 3128 -s 172.20.0.2 -j ACCEPT # interno
iptables -A INPUT -p tcp --dport 3128 -s 172.21.0.2 -j ACCEPT # esterno
iptables -A INPUT -p tcp --dport 3128 -s 172.22.0.2 -j ACCEPT # wifi
iptables -A INPUT -p tcp --dport 3128 -j DROP

# 7️⃣ REDIRECT (transparent proxy) — intercetta richieste al PEP (porta 3100)
iptables -t nat -A PREROUTING -s 172.20.0.2 -p tcp --dport 3100 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -s 172.21.0.2 -p tcp --dport 3100 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -s 172.22.0.2 -p tcp --dport 3100 -j REDIRECT --to-port 3128

# 8️⃣ Permetti al PEP di accedere al DB
iptables -A FORWARD -s 172.24.0.3 -d 172.25.0.4 -p tcp --dport 5432 -j ACCEPT
iptables -A FORWARD -p tcp --dport 5432 -j DROP

# 9️⃣ Permetti FORWARD al PEP per completare il flusso NAT
iptables -A FORWARD -s 172.20.0.2 -d 172.24.0.3 -p tcp --dport 3100 -j ACCEPT
iptables -A FORWARD -s 172.21.0.2 -d 172.24.0.3 -p tcp --dport 3100 -j ACCEPT
iptables -A FORWARD -s 172.22.0.2 -d 172.24.0.3 -p tcp --dport 3100 -j ACCEPT
iptables -A FORWARD -p tcp --dport 3100 -j DROP

echo "[Gateway] Regole iptables configurate."
