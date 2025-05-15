#!/bin/bash
set -e

# Avvia rsyslog (ignora errore se già avviato)
service rsyslog start || true

# Gestione più robusta del PID file
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

# Pulisci eventuali lock file esistenti
if [ -f /var/run/squid.pid ]; then
    rm -f /var/run/squid.pid
fi

# Inizializza cache solo se non già inizializzata
if [ ! -d /var/spool/squid/00 ]; then
    echo "Inizializzo cache Squid..."
    squid -z
fi

# Assicurati che le directory di log esistano e abbiano i permessi corretti
mkdir -p /var/log/squid
chown -R proxy:proxy /var/log/squid
chmod 755 /var/log/squid

# Avvia squid in modalità foreground
echo "Avvio Squid..."
squid -NYCd 1 &
SQUID_PID=$!

# Abilita IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Pulisci regole iptables esistenti per evitare duplicazioni
iptables -t nat -F POSTROUTING
iptables -t nat -F PREROUTING

# Configura NAT (MASQUERADE)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Reindirizzamento HTTP
iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 3128

# Aggiungi regole per le altre interfacce
iptables -t nat -A PREROUTING -i eth2 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth3 -p tcp --dport 80 -j REDIRECT --to-port 3128

echo "Setup completato con successo!"

# Mantieni il container attivo monitorando Squid
while true; do
    if ! ps -p $SQUID_PID > /dev/null; then
        echo "Squid è terminato, riavvio..."
        squid -NYCd 1 &
        SQUID_PID=$!
    fi
    sleep 10
done