#!/bin/bash

# Imposta default gateway alla IP del router sulla rete external-net
ip route del default 2>/dev/null
ip route add default via 172.21.0.3

# Avvia bash in foreground per poter interagire
exec "$@"