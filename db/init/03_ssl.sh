#!/bin/bash
set -e

# Copia i cert dove vuoi, con permessi corretti
cp /certs/server.crt /var/lib/postgresql/server.crt
cp /certs/server.key /var/lib/postgresql/server.key
chown postgres:postgres /var/lib/postgresql/server.key
chmod 600 /var/lib/postgresql/server.key

# Abilita SSL *dopo* initdb, modificando postgresql.conf
{
  echo "ssl = on"
  echo "ssl_cert_file = '/var/lib/postgresql/server.crt'"
  echo "ssl_key_file  = '/var/lib/postgresql/server.key'"
} >> "$PGDATA/postgresql.conf"

# Hostssl in pg_hba.conf
echo "hostssl all all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"