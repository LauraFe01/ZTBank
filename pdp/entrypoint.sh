#!/usr/bin/env bash
set -e

# Path al file di blacklist
BLACKLIST="/app/data/blacklist/blacklist.txt"

# Se il file esiste, lo svuoto in un solo comando
if [ -f "$BLACKLIST" ]; then
  echo "Svuotamento della blacklist in corso..."
  : > "$BLACKLIST"
  echo "Blacklist svuotata."
else
  echo "Attenzione: file blacklist non trovato in $BLACKLIST"
fi

exec "$@"
