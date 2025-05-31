#!/bin/bash
set -e

echo "=== Avvio script start.sh ==="

#### SQUID #####

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

# Avvia Squid in foreground
echo "Avvio Squid..."
squid -NYCd 1 &
SQUID_PID=$!

# Loop per tenere vivo il container monitorando Squid
while true; do
    if ! ps -p $SQUID_PID > /dev/null; then
        echo "Squid è terminato, riavvio..."
        squid -NYCd 1 &
        SQUID_PID=$!
    fi
    sleep 10
done

##########################
# 3. Preparazione Snort  #
##########################

# Array delle interfacce da monitorare
interfaces=("eth0" "eth1" "eth2" "eth3")

# Funzione per controllare se interfaccia è UP
is_interface_up() {
  ip link show "$1" | grep -q "state UP"
  return $?
}

# Funzione per creare directory log con permessi corretti
prepare_log_dir() {
  local dir="/var/log/snort/$1"
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo "Creata directory log $dir"
  fi
  chmod 755 "$dir"
}

# Avvio Snort per ogni interfaccia UP
for intf in "${interfaces[@]}"
do
  if is_interface_up "$intf"; then
    prepare_log_dir "$intf"
    echo "Avvio Snort su $intf..."
    snort -i "$intf" -A fast -c "/etc/snort/snort_${intf}.conf" -l "/var/log/snort/$intf" > /var/log/snort/snort_$intf.log 2>&1 &
    if [ $? -eq 0 ]; then
      echo "Snort avviato con successo su $intf"
    else
      echo "Errore nell'avvio di Snort su $intf"
    fi
  else
    echo "Interfaccia $intf DOWN, salto avvio Snort"
  fi
done

echo "Setup di SNORT completato con successo!"

##########################
# 6. Configurazione IP   #
##########################

### IPTABLES ###

# Nel container router, le interfacce di rete (eth0, eth1, eth2, eth3) corrispondono alle reti Docker:
# - eth0: external-net (192.168.20.0/24)
# - eth1: internal-net (192.168.10.0/24)
# - eth2: net-lab (192.168.200.0/24)
# - eth3: wifi-lan (192.168.30.0/24)

# 1. Abilita IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.conf.all.forwarding=1

echo "[Gateway] Avvio iptables..."

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

# Attesa attiva finché il DNS Docker risolve correttamente
echo "[Gateway] Attendo che internal_client sia raggiungibile..."
while true; do
  INT_IP=$(getent hosts internal_client | awk '{ print $1 }')
  if [[ -n "$INT_IP" ]]; then break; fi
  sleep 1
done
echo "[Gateway] IP di internal_client: $INT_IP"

echo "[Gateway] Attendo che external_client sia raggiungibile..."
while true; do
  EXT_IP=$(getent hosts external_client | awk '{ print $1 }')
  if [[ -n "$EXT_IP" ]]; then break; fi
  sleep 1
done
echo "[Gateway] IP di external_client: $EXT_IP"

# Rimuove eventuali zeri iniziali (es. 172.18.0.04 → 172.18.0.4)
INT_IP=$(echo "$INT_IP" | sed 's/\b0\+\([0-9]\)/\1/g')
EXT_IP=$(echo "$EXT_IP" | sed 's/\b0\+\([0-9]\)/\1/g')

# Permetti solo internal_client
iptables -A INPUT -s "$INT_IP" -j ACCEPT

# Mostra le regole attive
echo "[INFO] Regole attive:"
iptables -L -n

# exit 0

#################################
# 7. Avvio Applicazione Flask   #
#################################

# # Avvia l'applicazione Flask
# echo "Avvio Flask server..."
# python3 /router/api/app.py 

# echo "Setup di FLASK completato con successo!"

# Mantiene il container attivo
tail -f /dev/null
