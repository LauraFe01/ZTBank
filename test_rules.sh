#!/bin/bash
# Test delle regole iptables nel container gateway
# 1) aprire la git bash
# 2) rendere lo script eseguibile: chmod +x test_rules.sh
# 3) eseguire lo script: ./test_rules.sh
echo "🧪 TEST: Regole iptables nel container gateway"

# Test da internal_client (dovrebbe passare)
echo "- internal_client ➡ gateway (ping):"
docker exec internal_client ping -c 1 gateway >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ PASS: internal_client riesce a pingare gateway"
else
  echo "❌ FAIL: internal_client NON riesce a pingare gateway"
fi

# Test da external_client (dovrebbe essere bloccato)
echo "- external_client ➡ gateway (ping):"
docker exec external_client ping -c 1 gateway >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "❌ FAIL: external_client riesce a pingare gateway (NON dovrebbe)"
else
  echo "✅ PASS: external_client NON riesce a pingare gateway (come previsto)"
fi
