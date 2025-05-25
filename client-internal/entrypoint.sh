#!/bin/bash

# Imposta default gateway alla IP del router sulla rete internal-net
ip route del default 2>/dev/null
ip route add default via 192.168.10.254

# Avvia bash in foreground per poter interagire
exec "$@"
