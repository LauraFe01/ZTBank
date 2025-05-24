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

# Avvia Squid in foreground
echo "Avvio Squid..."
squid -NYCd 1 &

echo "Setup completato con successo!"

# Mantiene il container attivo
tail -f /dev/null
