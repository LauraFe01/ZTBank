#!/bin/bash

# Avvia rsyslog
service rsyslog start

# Aggiungi una regola iptables che logga il traffico (es. FORWARD chain)
iptables -A FORWARD -j LOG --log-prefix "ROUTER-LOG: " --log-level 4

# Mostra in tempo reale i log di sistema
tail -F /var/log/syslog
