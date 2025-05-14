#!/bin/bash

# Avvio di rsyslog
service rsyslog start

# Aggiunta di una regola iptables che logga il traffico
iptables -A FORWARD -j LOG --log-prefix "ROUTER-LOG: " --log-level 4

# Mostra in tempo reale i log di sistema
tail -F /var/log/syslog

#!/bin/bash

# Avvio di rsyslog
#service rsyslog start

# Aggiunta di regole iptables per logging e proxy
#iptables -A FORWARD -j LOG --log-prefix "ROUTER-LOG: " --log-level 4
#iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 3128

# Avvio di Snort
#snort -c /etc/snort/snort.conf -i eth0 &

# Avvio di Squid
#service squid start

# Mostra in tempo reale i log di sistema
#tail -f /var/log/syslog /var/log/snort/alert /var/log/squid/access.log
