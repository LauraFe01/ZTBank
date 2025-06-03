#!/bin/bash
set -e

echo "[Entrypoint] Cleanup completo processi Squid..."

# 1) Termina tutti i processi squid esistenti (più aggressivo)
killall squid 2>/dev/null || true
pkill -9 -f squid 2>/dev/null || true
pkill -9 -f "/usr/sbin/squid" 2>/dev/null || true

# 2) Rimuovi tutti i possibili file PID
rm -f /run/squid.pid
rm -f /var/run/squid.pid
rm -f /var/run/squid/*.pid 2>/dev/null || true

# 3) Aspetta più tempo per essere sicuri
sleep 5

# 4) Verifica finale e forza terminazione se necessario
if pgrep -f squid > /dev/null; then
    echo "[Entrypoint] ERRORE: Processi Squid ancora attivi, termino con SIGKILL..."
    pgrep -f squid | xargs kill -9 2>/dev/null || true
    sleep 3
fi

# 5) Mostra i processi attivi per debug
echo "[Entrypoint] Processi attivi:"
ps aux | grep squid || echo "Nessun processo squid trovato"

# Ho disattivato momentaneamente la cache per fare dei test perchè secondo chat se squid gestisce richieste uguali utilizzando la cache
# potrebbe impedire a snort di rilevare il traffico, non so se è na cazzata :)

# # 6) Inizializza cache solo se necessario
# if [ ! -d /var/spool/squid/00 ]; then
#     echo "[Entrypoint] Inizializzo la cache di Squid..."
#     squid -z
# fi

###################
## AVVIO IPTABLES #
###################

echo "[Entrypoint] Configuro iptables..."
/opt/rules.sh &

# 8) Ultimo controllo prima di avviare Squid
if [ -f /run/squid.pid ]; then
    echo "[Entrypoint] File PID ancora presente, lo rimuovo..."
    rm -f /run/squid.pid
fi

########################
## AVVIO BLACKLIST.SH ##
########################

echo "[Entrypoint] Avvio apply_blacklist.sh in background..."
/opt/apply_blacklist.sh &

#################
## AVVIO SNORT ##
#################

for iface in eth0 eth1 eth2 eth3; do
  echo "[INFO] Avvio Snort su $iface"
  snort -i "$iface" -c /etc/snort/snort.conf -A full -k none -l /var/log/snort -v > "/var/log/snort/snort_${iface}.log" 2>&1 &
done

#################
## AVVIO SQUID ##
#################

# Quando si usa exec in bash, quel comando sostituisce il processo corrente. Di conseguenza, il codice che segue non viene mai eseguito.
# (quindi va messo per ultimo)
echo "[Entrypoint] Avvio Squid in foreground..."
exec squid -N -d 1