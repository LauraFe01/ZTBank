#!/usr/bin/env python3
import requests
import json
import time
import sys
import argparse
from datetime import datetime

def print_status(message, status="info"):
    """Stampa un messaggio formattato con il suo stato"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if status == "success":
        prefix = "✅"
    elif status == "error":
        prefix = "❌"
    elif status == "warning":
        prefix = "⚠️"
    else:
        prefix = "ℹ️"
    
    print(f"{prefix} [{timestamp}] {message}")

def monitor_trust_scores(base_url, target_ip=None, interval=10, duration=300):
    """
    Monitora i punteggi di fiducia e gli IP bloccati in tempo reale
    """
    start_time = time.time()
    end_time = start_time + duration
    iteration = 1
    
    print_status(f"Avvio monitoraggio della policy di sicurezza")
    print_status(f"Durata: {duration} secondi, intervallo: {interval} secondi")
    
    if target_ip:
        print_status(f"Monitoraggio specifico per IP: {target_ip}")
    
    # Salva lo stato iniziale per confronto
    initial_blocked_ips = get_blocked_ips(base_url)
    
    try:
        while time.time() < end_time:
            print(f"\n{'='*60}")
            print_status(f"Controllo #{iteration} - Tempo trascorso: {int(time.time() - start_time)}s")
            
            # Controlla IP bloccati
            blocked_ips = get_blocked_ips(base_url)
            
            # Verifica punteggi di fiducia
            trust_scores = get_trust_scores(base_url)
            
            # Mostra nuovi IP bloccati da quando è iniziato il monitoraggio
            new_blocked = [ip for ip in blocked_ips if ip not in initial_blocked_ips]
            if new_blocked:
                print_status(f"Nuovi IP bloccati durante il monitoraggio: {', '.join(new_blocked)}", "warning")
            
            # Se è specificato un IP target, monitora specificamente quello
            if target_ip:
                target_score = next((score for score in trust_scores if score.get('ip') == target_ip), None)
                target_blocked = target_ip in blocked_ips
                
                if target_score:
                    block_status = "BLOCCATO" if target_blocked else "non bloccato"
                    print_status(f"IP Target {target_ip}: Score {target_score.get('current_score')}/100 - {block_status}")
                    
                    # Se un IP bloccato ha eventi recenti, stampali
                    if target_blocked:
                        get_recent_events(base_url, target_ip)
                else:
                    print_status(f"IP Target {target_ip} non trovato nel database dei punteggi", "warning")
            
            # Attendi prima del prossimo controllo
            iteration += 1
            if time.time() + interval < end_time:
                time.sleep(interval)
            else:
                break
        
        print(f"\n{'='*60}")
        print_status(f"Monitoraggio completato dopo {int(time.time() - start_time)} secondi", "success")
        
        # Stampa riepilogo finale
        print_summary(base_url, initial_blocked_ips)
        
    except KeyboardInterrupt:
        print_status("\nMonitoraggio interrotto dall'utente")
        # Stampa comunque un riepilogo
        print_summary(base_url, initial_blocked_ips)
    except Exception as e:
        print_status(f"Errore durante il monitoraggio: {str(e)}", "error")

def get_blocked_ips(base_url):
    """Ottiene la lista degli IP attualmente bloccati"""
    try:
        response = requests.get(f"{base_url}/blocked-ips", timeout=5)
        if response.status_code == 200:
            return response.json().get('blocked_ips', [])
        else:
            print_status(f"Errore nel recupero degli IP bloccati: {response.status_code}", "error")
            return []
    except Exception as e:
        print_status(f"Errore di connessione: {str(e)}", "error")
        return []

def get_trust_scores(base_url):
    """Ottiene i punteggi di fiducia di tutti gli IP"""
    try:
        response = requests.get(f"{base_url}/trust-scores", timeout=5)
        if response.status_code == 200:
            scores = response.json().get('trust_scores', [])
            
            # Stampa IP con punteggio di fiducia basso (< 50)
            low_trust = [s for s in scores if s.get('current_score', 100) < 50]
            if low_trust:
                print_status(f"IP con basso punteggio di fiducia:")
                for score in sorted(low_trust, key=lambda x: x.get('current_score', 0)):
                    block_status = "BLOCCATO" if score.get('blocked') else "non bloccato"
                    print(f"  - {score.get('ip')}: {score.get('current_score')}/100 - {block_status}")
                    if score.get('block_reason'):
                        print(f"    Motivo: {score.get('block_reason')}")
            else:
                print_status("Nessun IP con punteggio di fiducia basso")
                
            return scores
        else:
            print_status(f"Errore nel recupero dei punteggi: {response.status_code}", "error")
            return []
    except Exception as e:
        print_status(f"Errore di connessione: {str(e)}", "error")
        return []

def get_recent_events(base_url, ip=None):
    """Ottiene gli eventi recenti per un IP specifico"""
    try:
        response = requests.get(f"{base_url}/trust-scores", timeout=5)
        if response.status_code == 200:
            events = response.json().get('recent_events', [])
            
            if ip:
                # Filtra per IP specifico
                ip_events = [e for e in events if e.get('ip') == ip]
                if ip_events:
                    print_status(f"Eventi recenti per {ip}:")
                    for event in ip_events[:5]:  # Mostra solo i 5 più recenti
                        impact = event.get('score_impact', 0)
                        impact_str = f"+{impact}" if impact > 0 else str(impact)
                        print(f"  - {event.get('timestamp')}: {event.get('description')} ({impact_str} punti)")
                return ip_events
            else:
                return events
        else:
            print_status(f"Errore nel recupero degli eventi: {response.status_code}", "error")
            return []
    except Exception as e:
        print_status(f"Errore di connessione: {str(e)}", "error")
        return []

def print_summary(base_url, initial_blocked_ips):
    """Stampa un riepilogo finale del monitoraggio"""
    print(f"\n{'='*60}")
    print_status("RIEPILOGO MONITORAGGIO", "info")
    
    # Ottieni lo stato attuale
    current_blocked_ips = get_blocked_ips(base_url)
    
    # Calcola le differenze
    new_blocked = [ip for ip in current_blocked_ips if ip not in initial_blocked_ips]
    
    # Stampa il riepilogo
    print_status(f"IP bloccati all'inizio: {len(initial_blocked_ips)}")
    print_status(f"IP bloccati alla fine: {len(current_blocked_ips)}")
    
    if new_blocked:
        print_status(f"Nuovi IP bloccati durante il monitoraggio: {len(new_blocked)}", "warning")
        for ip in new_blocked:
            print(f"  - {ip}")
            get_recent_events(base_url, ip)
    else:
        print_status("Nessun nuovo IP bloccato durante il monitoraggio", "info")

def main():
    parser = argparse.ArgumentParser(description='Monitora i punteggi di fiducia e gli IP bloccati')
    parser.add_argument('-u', '--url', default='http://192.168.200.254:5000', help='URL base del servizio router (default: http://192.168.200.254:5000)')
    parser.add_argument('-t', '--target-ip', help='IP specifico da monitorare')
    parser.add_argument('-i', '--interval', type=int, default=10, help='Intervallo in secondi tra i controlli (default: 10)')
    parser.add_argument('-d', '--duration', type=int, default=300, help='Durata totale del monitoraggio in secondi (default: 300)')
    
    args = parser.parse_args()
    
    monitor_trust_scores(args.url, args.target_ip, args.interval, args.duration)

if __name__ == "__main__":
    main()