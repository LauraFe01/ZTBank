#!/bin/bash
set -e

echo "=== Avvio script start.sh ==="


##########################
# 2. Preparazione Squid  #
##########################

# Assicura permessi log Squid
mkdir -p /var/log/squid
chown -R proxy:proxy /var/log/squid
chmod 755 /var/log/squid

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

# Avvia Squid in foreground
echo "Avvio Squid..."
squid -NYCd 1 &

echo "Setup di SQUID completato con successo!"

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

# 2. Pulisci tutte le regole precedenti
iptables -F
iptables -t nat -F
iptables -t mangle -F

# 3. Imposta policy di default
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 4. Permetti loopback (IMPORTANTE)
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 5. Permetti connessioni ESTABLISHED,RELATED
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# 6. Regole NAT - PREROUTING per redirect HTTP a Squid (proxy trasparente)
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 3128
iptables -t nat -A PREROUTING -i eth3 -p tcp --dport 80 -j REDIRECT --to-port 3128

# SNAT per traffico da ciascuna rete client verso il DB (192.168.200.10) nella rete net-lab
# iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -d 192.168.200.0/24 -o eth2 -j SNAT --to-source 192.168.200.254
# iptables -t nat -A POSTROUTING -s 192.168.20.0/24 -d 192.168.200.0/24 -o eth2 -j SNAT --to-source 192.168.200.254
# iptables -t nat -A POSTROUTING -s 192.168.30.0/24 -d 192.168.200.0/24 -o eth2 -j SNAT --to-source 192.168.200.254

# # 8. Consenti traffico ICMP (ping) su INPUT e FORWARD
# iptables -A INPUT -p icmp -j ACCEPT
# iptables -A FORWARD -p icmp -j ACCEPT

# # 9. FORWARD - traffico verso DB PostgreSQL (porta 5432)
# iptables -A FORWARD -p tcp -d 192.168.200.10 --dport 5432 -j ACCEPT
# iptables -A FORWARD -p tcp -s 192.168.200.10 --sport 5432 -j ACCEPT

# # 11. FORWARD - traffico tra client e rete DB (bidirezionale)
# iptables -A FORWARD -s 192.168.10.0/24 -d 192.168.200.0/24 -j ACCEPT
# iptables -A FORWARD -s 192.168.200.0/24 -d 192.168.10.0/24 -j ACCEPT

# iptables -A FORWARD -s 192.168.20.0/24 -d 192.168.200.0/24 -j ACCEPT
# iptables -A FORWARD -s 192.168.200.0/24 -d 192.168.20.0/24 -j ACCEPT

# iptables -A FORWARD -s 192.168.30.0/24 -d 192.168.200.0/24 -j ACCEPT
# iptables -A FORWARD -s 192.168.200.0/24 -d 192.168.30.0/24 -j ACCEPT

# # 12. Consenti traffico DNS (porta 53 UDP/TCP) per risoluzione nomi
# iptables -A FORWARD -p udp --dport 53 -j ACCEPT
# iptables -A FORWARD -p tcp --dport 53 -j ACCEPT


#################################
# 7. Avvio Applicazione Flask   #
#################################

# Avvia l'applicazione Flask
echo "Avvio Flask server..."
python3 /router/api/app.py 

echo "Setup di FLASK completato con successo!"

# Mantiene il container attivo
tail -f /dev/null
