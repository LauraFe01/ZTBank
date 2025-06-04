#!/bin/bash
set -e

echo "[INFO] Configurazione SSL per PostgreSQL in corso..."

# Percorsi certificati
CERT_SRC_DIR="/certs"
CERT_DST_DIR="/var/lib/postgresql"

# Copia certificati
cp "${CERT_SRC_DIR}/server.crt" "${CERT_DST_DIR}/server.crt"
cp "${CERT_SRC_DIR}/server.key" "${CERT_DST_DIR}/server.key"

# Setta permessi corretti
chown postgres:postgres "${CERT_DST_DIR}/server.key" "${CERT_DST_DIR}/server.crt"
chmod 600 "${CERT_DST_DIR}/server.key"
chmod 644 "${CERT_DST_DIR}/server.crt"

echo "[INFO] Certificati copiati e permessi impostati."

# Abilita SSL nel file postgresql.conf
{
  echo ""
  echo "# Abilitazione SSL"
  echo "ssl = on"
  echo "ssl_cert_file = '${CERT_DST_DIR}/server.crt'"
  echo "ssl_key_file  = '${CERT_DST_DIR}/server.key'"
} >> "$PGDATA/postgresql.conf"

echo "[INFO] postgresql.conf aggiornato con impostazioni SSL."

# Aggiunge hostssl a pg_hba.conf se non già presente
if ! grep -q "hostssl all all" "$PGDATA/pg_hba.conf"; then
  echo "hostssl all all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"
  echo "[INFO] hostssl aggiunto a pg_hba.conf."
else
  echo "[INFO] hostssl già presente in pg_hba.conf, nessuna modifica."
fi

echo "[INFO] Configurazione SSL completata."