#!/bin/bash
set -e

# Avvia rsyslog (ignora errore se già avviato)
service rsyslog start || true

# Gestione robusta PID Squid
if [ -f /run/squid.pid ]; then
    PID=$(cat /run/squid.pid)
    if ! ps -p "$PID" >/dev/null 2>&1; then
        echo "PID file esistente ma processo non attivo. Lo rimuovo."
        rm -f /run/squid.pid
    else
        echo "Termino istanza precedente di Squid con PID $PID."
        kill "$PID"
        sleep 2
        if ps -p "$PID" >/dev/null 2>&1; then
            kill -9 "$PID"
            sleep 1
        fi
        rm -f /run/squid.pid
    fi
fi

# Pulisce eventuali lock file
rm -f /var/run/squid.pid || true

# Inizializza cache se necessario
if [ ! -d /var/spool/squid/00 ]; then
    echo "Inizializzo cache Squid..."
    squid -z
fi

# Assicura permessi log Squid
mkdir -p /var/log/squid
chown -R proxy:proxy /var/log/squid
chmod 755 /var/log/squid

# Assicura log Snort
mkdir -p /var/log/snort
chmod 755 /var/log/snort

# Avvia Snort
echo "Avvio Snort..."
snort -i eth1 -A fast -c /etc/snort/snort.conf -l /var/log/snort > /var/log/snort/snort.log 2>&1 & # in alternativa snort -i any

# Avvia Squid in foreground
echo "Avvio Squid..."
squid -NYCd 1 &
SQUID_PID=$!

# Abilita IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Reset iptables
iptables -t nat -F POSTROUTING
iptables -t nat -F PREROUTING

# Default: nega l’accesso al DB (porta 5432), in uanto dobbiamo controllare dinamicamente chi può accedere
iptables -A FORWARD -p tcp --dport 5432 -j DROP
# Avvia il demone di controllo delle policy
python3 /policy_enforcer.py &

# NAT e redirect HTTP verso Squid
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth2 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth3 -p tcp --dport 80 -j REDIRECT --to-port 3128

echo "Setup completato con successo!"

# Loop per tenere vivo il container monitorando Squid
while true; do
    if ! ps -p $SQUID_PID > /dev/null; then
        echo "Squid è terminato, riavvio..."
        squid -NYCd 1 &
        SQUID_PID=$!
    fi
    sleep 10
done
