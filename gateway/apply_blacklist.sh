#!/bin/bash

BLACKLIST_FILE="/app/blacklist/blacklist.txt"
touch "$BLACKLIST_FILE"

echo "[Blacklist] Inizio monitoraggio"

while inotifywait -e modify "$BLACKLIST_FILE"; do
  while read -r ip; do
    if [ -n "$ip" ]; then
      iptables -C INPUT -s "$ip" -j REJECT 2>/dev/null || iptables -I INPUT 1 -s "$ip" -j REJECT
      echo "[Blacklist] IP $ip bloccato"
    fi
  done < "$BLACKLIST_FILE"
done