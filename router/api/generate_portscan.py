#!/usr/bin/env python3
import socket
import random
import time
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor

def scan_port(target_ip, port):
    """Tenta di connettersi a una porta su un IP target"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)
    try:
        sock.connect((target_ip, port))
        sock.close()
        return port, True
    except (socket.timeout, socket.error):
        sock.close()
        return port, False

def scan_ports(target_ip, num_ports=15, delay=0.2):
    """Esegue una scansione di un numero specificato di porte"""
    # Scegli porte casuali tra le più comuni
    common_ports = [21, 22, 23, 25, 53, 80, 110, 119, 123, 143, 443, 465, 587, 993, 995,
                   1080, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 9000]
    
    # Se il numero di porte richieste è maggiore delle porte comuni disponibili, aggiungi porte casuali
    ports_to_scan = random.sample(common_ports, min(num_ports, len(common_ports)))
    
    if num_ports > len(common_ports):
        # Aggiungi porte casuali fino a raggiungere il numero richiesto
        while len(ports_to_scan) < num_ports:
            port = random.randint(1025, 65535)
            if port not in ports_to_scan:
                ports_to_scan.append(port)
    
    print(f"[*] Avvio scansione di {num_ports} porte sull'IP {target_ip}")
    
    # Esegui la scansione in parallelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = []
        for port in ports_to_scan:
            results.append(executor.submit(scan_port, target_ip, port))
            time.sleep(delay)  # Aggiungi un piccolo ritardo tra le connessioni
        
        # Raccogli i risultati
        open_ports = []
        for future in results:
            port, is_open = future.result()
            status = "aperta" if is_open else "chiusa"
            print(f"[*] Porta {port}: {status}")
            if is_open:
                open_ports.append(port)
    
    print(f"[+] Scansione completata. Porte aperte trovate: {len(open_ports)}")
    return open_ports

def main():
    parser = argparse.ArgumentParser(description='Tool per generare scansioni di porte per testing di sicurezza')
    parser.add_argument('target', help='Indirizzo IP target da scansionare')
    parser.add_argument('-n', '--num-scans', type=int, default=3, help='Numero di scansioni da eseguire (default: 3)')
    parser.add_argument('-p', '--ports', type=int, default=15, help='Numero di porte da scansionare per ciclo (default: 15)')
    parser.add_argument('-d', '--delay', type=float, default=0.2, help='Ritardo tra le connessioni in secondi (default: 0.2)')
    parser.add_argument('-i', '--interval', type=int, default=5, help='Intervallo in secondi tra le scansioni (default: 5)')
    
    args = parser.parse_args()
    
    print(f"[*] Test di sicurezza - Generazione di eventi per Snort")
    print(f"[*] Target: {args.target}")
    print(f"[*] Esecuzione di {args.num_scans} scansioni con {args.ports} porte ciascuna")
    
    try:
        for i in range(args.num_scans):
            print(f"\n[*] Scansione {i+1}/{args.num_scans}")
            scan_ports(args.target, args.ports, args.delay)
            
            if i < args.num_scans - 1:
                print(f"[*] Attesa di {args.interval} secondi prima della prossima scansione...")
                time.sleep(args.interval)
        
        print("\n[+] Generazione eventi completata con successo!")
        
    except KeyboardInterrupt:
        print("\n[-] Scansione interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Errore durante la scansione: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()