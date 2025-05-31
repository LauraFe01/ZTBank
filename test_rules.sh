#!/bin/bash

set -e

echo "🔍 Verifica Squid in esecuzione nel container 'gateway'..."
docker exec gateway ps aux | grep [s]quid || { echo "❌ Squid non è in esecuzione"; exit 1; }


echo "🌐 Test da internal_client (dovrebbe riuscire)..."
docker exec internal_client curl -s -o /dev/null -w "%{http_code}\n" -x http://gateway:3128 http://example.com

echo "❌ Test da external_client (dovrebbe fallire o rimanere appeso)..."
docker exec external_client timeout 5 curl -s -o /dev/null -w "%{http_code}\n" -x http://gateway:3128 http://example.com || echo "(nessuna risposta)"

echo "📜 Ultime 10 righe del log access_log di Squid:"
docker exec gateway tail -n 10 /var/log/squid/access.log
