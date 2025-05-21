import requests
import json
import time

# === CONFIGURAZIONE WEBHOOK ===
webhook_url = "http://localhost:5000/splunk-webhook-db"  # URL del container router

# Casi di test basati sui dati reali del database
webhook_test_cases = [
    # Test per cassiere (alice)
    {
        "username": "alice", 
        "file_name": "conto_corrente_2024.txt", 
        "azione": "lettura",
        "description": "Alice (cassiere) tenta di leggere file sensibile"
    },
    {
        "username": "alice", 
        "file_name": "offerte_promozionali.txt", 
        "azione": "lettura",
        "description": "Alice (cassiere) tenta di leggere file non sensibile (dovrebbe essere consentito)"
    },
    {
        "username": "alice", 
        "file_name": "offerte_promozionali.txt", 
        "azione": "scrittura",
        "description": "Alice (cassiere) tenta di scrivere su file non sensibile (dovrebbe essere negato)"
    },
    
    # Test per manager (bob)
    {
        "username": "bob", 
        "file_name": "conto_corrente_2024.txt", 
        "azione": "scrittura",
        "description": "Bob (manager) tenta di scrivere file sensibile (dovrebbe essere consentito)"
    },
    {
        "username": "bob", 
        "file_name": "offerte_promozionali.txt", 
        "azione": "scrittura",
        "description": "Bob (manager) tenta di scrivere file non sensibile (dovrebbe essere consentito)"
    },
    
    # Test per auditor (carol)
    {
        "username": "carol", 
        "file_name": "log_sicurezza.txt", 
        "azione": "lettura",
        "description": "Carol (auditor) tenta di leggere log sensibile (dovrebbe essere consentito se inizia con 'log_')"
    },
    {
        "username": "carol", 
        "file_name": "conto_corrente_2024.txt", 
        "azione": "lettura",
        "description": "Carol (auditor) tenta di leggere file sensibile non log (dovrebbe essere negato)"
    },
    {
        "username": "carol", 
        "file_name": "log_sicurezza.txt", 
        "azione": "scrittura",
        "description": "Carol (auditor) tenta di scrivere su log (dovrebbe essere negato)"
    }
]

# === TEST WEBHOOK ===
def test_webhook():
    print("\n=== TEST WEBHOOK CONTROLLO ACCESSI ===\n")
    
    for i, test_case in enumerate(webhook_test_cases):
        # Estrai la descrizione e rimuovila dai dati da inviare
        description = test_case.pop("description", "Nessuna descrizione")
        
        print(f"\n[TEST #{i+1}] {description}")
        print(f"Dati: {json.dumps(test_case, indent=2)}")
        
        try:
            # Invia la richiesta alla webhook
            start_time = time.time()
            response = requests.post(
                webhook_url,
                headers={"Content-Type": "application/json"},
                json=test_case,  # Usa json invece di data per gestire automaticamente la conversione
                timeout=5  # Timeout di 5 secondi
            )
            elapsed = time.time() - start_time
            
            print(f"Status code: {response.status_code} (richiesta completata in {elapsed:.2f}s)")
            
            # Analizza la risposta
            try:
                result = response.json()
                print(f"Risposta: {json.dumps(result, indent=2)}")
                
                # Analisi del risultato
                if "accesso_concesso" in result:
                    if result["accesso_concesso"]:
                        print(f"✓ ACCESSO CONCESSO: {result.get('motivazione', '')}")
                    else:
                        print(f"✗ ACCESSO NEGATO: {result.get('motivazione', '')}")
                elif "error" in result:
                    print(f"! ERRORE: {result['error']}")
                else:
                    print(f"! Risposta inaspettata.")
            except json.JSONDecodeError:
                print(f"! Impossibile decodificare la risposta JSON: {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"! ERRORE: Impossibile connettersi al server. Verifica che il container router sia attivo.")
        except requests.exceptions.Timeout:
            print(f"! ERRORE: Timeout nella richiesta. Il server sta impiegando troppo tempo per rispondere.")
        except Exception as e:
            print(f"! ERRORE: {str(e)}")
        
        # Rimetti la descrizione nel test case per il prossimo ciclo
        test_case["description"] = description
        
        # Pausa tra le richieste per non sovraccaricare il server
        time.sleep(0.5)

if __name__ == "__main__":
    print("Avvio del test della webhook per il controllo accessi...")
    test_webhook()
    print("\nTest completato.")