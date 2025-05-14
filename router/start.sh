#!/bin/bash

# Avvio di rsyslog
service rsyslog start

# Aggiunta di una regola iptables che logga il traffico
iptables -A FORWARD -j LOG --log-prefix "ROUTER-LOG: " --log-level 4

# Mostra in tempo reale i log di sistema
tail -F /var/log/syslog
