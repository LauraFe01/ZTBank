#!/bin/bash

BLACKLIST_FILE="/app/blacklist/blacklist.txt"
BLACKLIST_DIR="$(dirname "$BLACKLIST_FILE")"
touch "$BLACKLIST_FILE"

echo "[Blacklist] Inizio monitoraggio"

inotifywait -m -e modify,create,move,delete "$BLACKLIST_DIR" | while read -r directory events filename; do
  if [[ "$filename" == "$(basename "$BLACKLIST_FILE")" ]]; then
    while read -r ip; do
      if [ -n "$ip" ]; then
        iptables -C INPUT -s "$ip" -j REJECT 2>/dev/null || iptables -I INPUT 1 -s "$ip" -j REJECT
        echo "[Blacklist] IP $ip bloccato"
      fi
    done < "$BLACKLIST_FILE"
  fi
done
