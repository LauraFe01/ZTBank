#!/usr/bin/env python3
import requests
import json
import sys
import os

# Configurazione URL in base all'ambiente
if os.path.exists('/.dockerenv'):  # Siamo dentro un container
    BASE_URL = "http://localhost:5000"
else:  # Siamo fuori dal container
    BASE_URL = "http://192.168.200.254:5000"

def test_health_check():
    """Test dell'endpoint di health check"""
    print("=== Test Health Check ===")
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url, timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Errore: Impossibile connettersi a {url}")
        print("   Verifica che il container router sia in esecuzione")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_webhook():
    """Test del webhook con payload simulato di Splunk"""
    print("\n=== Test Webhook ===")
    url = f"{BASE_URL}/splunk-webhook"
    
    # Payload di esempio che simula quello inviato da Splunk
    test_payload = {
        "sid": "scheduler__admin__search__RMD5982c2343e5c1e1d2_at_1642089600_168",
        "search_name": "test_icmp_ping_alert",
        "owner": "admin",
        "app": "my_custom_alerts",
        "results_link": "http://splunk:8000/app/my_custom_alerts/search?sid=...",
        "results": [
            {
                "timestamp": "2025-05-19T20:58:00",
                "src_ip": "192.168.10.100",  # IP di test
                "dst_ip": "192.168.20.10"
            },
            {
                "timestamp": "2025-05-19T20:58:05", 
                "src_ip": "192.168.30.200",  # Altro IP di test
                "dst_ip": "192.168.200.10"
            }
        ]
    }
    
    try:
        response = requests.post(url, json=test_payload, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook processato con successo!")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Errore: Impossibile connettersi a {url}")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_legacy_endpoint():
    """Test dell'endpoint legacy per compatibilità"""
    print("\n=== Test Legacy Endpoint ===")
    url = f"{BASE_URL}/enforce"
    
    test_payload = {
        "ip": "192.168.10.50",  # IP di test
        "action": "block"
    }
    
    try:
        response = requests.post(url, json=test_payload, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Errore: Impossibile connettersi a {url}")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def check_blocked_ips():
    """Controlla la lista degli IP bloccati"""
    print("\n=== IP Bloccati ===")
    url = f"{BASE_URL}/blocked-ips"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            blocked_ips = response.json().get('blocked_ips', [])
            if blocked_ips:
                print(f"✅ IP bloccati ({len(blocked_ips)}):")
                for ip in blocked_ips:
                    print(f"   - {ip}")
            else:
                print("✅ Nessun IP bloccato al momento")
        else:
            print(f"❌ Status Code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Errore: Impossibile connettersi a {url}")
        return False
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

def test_multiple_alerts():
    """Test con multiple alert di diverso tipo"""
    print("\n=== Test Multiple Alert Types ===")
    url = f"{BASE_URL}/splunk-webhook"
    
    # Test alert per connessioni sospette
    suspicious_payload = {
        "search_name": "SuspiciousConnections",
        "results": [
            {
                "timestamp": "2025-05-19T21:00:00",
                "client_ip": "192.168.10.25",
                "url": "http://malware.example.com/payload",
                "method": "GET"
            }
        ]
    }
    
    # Test alert per accesso database
    db_access_payload = {
        "search_name": "DatabaseAccessAttempts", 
        "results": [
            {
                "timestamp": "2025-05-19T21:01:00",
                "src_ip": "192.168.30.100",
                "dst_ip": "192.168.200.10",
                "alert_type": "database_access_attempt"
            }
        ]
    }
    
    for name, payload in [("Suspicious Connection", suspicious_payload), 
                         ("Database Access", db_access_payload)]:
        try:
            response = requests.post(url, json=payload, timeout=10)
            print(f"✅ {name}: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ {name}: {e}")

def main():
    print("🔗 Test della configurazione webhook Splunk")
    print(f"🎯 Target URL: {BASE_URL}")
    print("─" * 60)
    
    # Test di connessione base
    if not test_health_check():
        print("\n❌ Health check fallito. Verifica che il servizio sia in esecuzione.")
        sys.exit(1)
    
    # Esegui tutti i test
    test_webhook()
    test_legacy_endpoint() 
    check_blocked_ips()
    test_multiple_alerts()
    
    print("\n─" * 60)
    print("✅ Test completati!")
    print("\n💡 Suggerimenti:")
    print("   - Controlla i log in /var/log/router/policy_enforcer.log")
    print("   - Verifica le regole iptables con: iptables -L")
    print("   - Monitora gli alert in Splunk Web")

if __name__ == "__main__":
    main()