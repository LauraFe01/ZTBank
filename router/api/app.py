#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json
import logging
import subprocess
from datetime import datetime, timedelta
import sqlite3
import os

# Questo file app.py contiene l'implementazione completa della policy di sicurezza basata sul sistema di fiducia.
# Nello specifico, implementa la Policy 8.2 sulla "Reputazione Storica delle Reti" discussa nel documento, che prevede una riduzione
# automatica della fiducia e un possibile blocco per gli IP che effettuano numerosi tentativi di attacco.
# Il codice include:

# 1. Un database SQLite per tracciare i punteggi di fiducia e gli eventi di sicurezza
# 2. Funzioni per gestire i punteggi di fiducia (inizializzazione, recupero, aggiornamento)
# 3. Logica per elaborare gli alert da Splunk relativi a tentativi di attacco
# 4. Endpoint aggiuntivi per visualizzare i punteggi di fiducia e gli eventi di sicurezza
# 5. Integrazione con le funzioni esistenti di blocco/sblocco degli IP

# Questo sistema permette di implementare un approccio di sicurezza basato sulla fiducia, come descritto nel documento di policy,
# dove gli IP che mostrano comportamenti sospetti vengono progressivamente penalizzati fino a un eventuale blocco completo quando
# la fiducia scende sotto la soglia critica.

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/router/policy_enforcer.log'),
        logging.StreamHandler()
    ]
)

# Crea una directory per il database se non esiste
os.makedirs('/var/log/router/db', exist_ok=True)

# Inizializza il database per tenere traccia dei punteggi di fiducia
def init_trust_db():
    """
    Inizializza il database SQLite per memorizzare i punteggi di fiducia degli IP
    """
    conn = sqlite3.connect('/var/log/router/db/trust_scores.db')
    c = conn.cursor()
    # Crea tabella per i punteggi di fiducia se non esiste
    c.execute('''
    CREATE TABLE IF NOT EXISTS trust_scores (
        ip TEXT PRIMARY KEY,
        base_score INTEGER DEFAULT 60,
        current_score INTEGER,
        last_updated TIMESTAMP,
        blocked INTEGER DEFAULT 0,
        block_reason TEXT,
        block_timestamp TIMESTAMP
    )
    ''')
    # Crea tabella per gli eventi di sicurezza se non esiste
    c.execute('''
    CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        event_type TEXT,
        description TEXT,
        score_impact INTEGER,
        timestamp TIMESTAMP,
        FOREIGN KEY (ip) REFERENCES trust_scores(ip)
    )
    ''')
    conn.commit()
    conn.close()

# Funzione per ottenere il punteggio di fiducia di un IP
def get_trust_score(ip):
    """
    Ottiene il punteggio di fiducia attuale per un IP specifico.
    Se l'IP non esiste nel database, lo inserisce con un punteggio base predefinito.
    """
    conn = sqlite3.connect('/var/log/router/db/trust_scores.db')
    c = conn.cursor()
    
    c.execute('SELECT current_score, blocked FROM trust_scores WHERE ip = ?', (ip,))
    result = c.fetchone()
    
    if result:
        score, blocked = result
        conn.close()
        return score, blocked == 1
    else:
        # IP non trovato, inserisci con punteggio base (assumiamo un client generico, 60 punti)
        base_score = 60  # Punteggio base per client generico come da policy
        c.execute(
            'INSERT INTO trust_scores (ip, base_score, current_score, last_updated) VALUES (?, ?, ?, ?)',
            (ip, base_score, base_score, datetime.now())
        )
        conn.commit()
        conn.close()
        return base_score, False

# Funzione per aggiornare il punteggio di fiducia di un IP
def update_trust_score(ip, score_change, reason):
    """
    Aggiorna il punteggio di fiducia di un IP e registra l'evento che ha causato il cambiamento.
    Se il punteggio scende sotto la soglia critica (25), l'IP viene segnalato per il blocco.
    """
    conn = sqlite3.connect('/var/log/router/db/trust_scores.db')
    c = conn.cursor()
    
    # Ottieni il punteggio attuale
    c.execute('SELECT current_score FROM trust_scores WHERE ip = ?', (ip,))
    result = c.fetchone()
    
    if result:
        current_score = result[0]
    else:
        # Se l'IP non esiste, ottieni il punteggio base e poi aggiornalo
        current_score, _ = get_trust_score(ip)
    
    # Calcola il nuovo punteggio
    new_score = max(0, min(100, current_score + score_change))  # Mantieni tra 0 e 100
    
    # Aggiorna il punteggio
    c.execute(
        'UPDATE trust_scores SET current_score = ?, last_updated = ? WHERE ip = ?',
        (new_score, datetime.now(), ip)
    )
    
    # Registra l'evento di sicurezza
    c.execute(
        'INSERT INTO security_events (ip, event_type, description, score_impact, timestamp) VALUES (?, ?, ?, ?, ?)',
        (ip, 'trust_score_change', reason, score_change, datetime.now())
    )
    
    conn.commit()
    
    # Determina se l'IP deve essere bloccato (score <= 25 come da policy 8.3)
    should_block = new_score <= 25
    
    if should_block:
        c.execute(
            'UPDATE trust_scores SET blocked = 1, block_reason = ?, block_timestamp = ? WHERE ip = ?',
            (reason, datetime.now(), ip)
        )
        conn.commit()
    
    conn.close()
    return new_score, should_block

# Funzione per processare gli alert di attacco da Splunk
def process_splunk_attack_alert(result):
    """
    Processa un alert da Splunk relativo a tentativi di attacco.
    Riduce il punteggio di fiducia dell'IP e lo blocca se necessario.
    """
    app.logger.info(f"Processando alert di attacco: {result}")
    
    # Estrai le informazioni dall'alert
    src_ip = result.get('src_ip')
    count = int(result.get('count', 0))
    risk_score = int(result.get('risk_score', 25))  # Default a 25 se non specificato
    reason = result.get('reason', 'Multiple attack attempts detected')
    
    if not src_ip:
        app.logger.warning("Alert senza IP sorgente, impossibile processare")
        return False
    
    # Applica la riduzione del punteggio di fiducia come da policy
    app.logger.info(f"Riducendo punteggio di fiducia per {src_ip} di {risk_score} punti: {reason}")
    new_score, should_block = update_trust_score(src_ip, -risk_score, reason)
    
    # Se l'IP deve essere bloccato o l'azione è esplicitamente "block"
    if should_block or result.get('action') == 'block':
        app.logger.info(f"Punteggio di fiducia critico ({new_score}) per {src_ip}, applicazione blocco")
        success = apply_block_policy(src_ip, result)
        return success
    
    return True

@app.route('/splunk-webhook', methods=['POST'])
def handle_splunk_webhook():
    """
    Gestisce i webhook provenienti da Splunk alerts
    Supporta la policy di reputazione storica delle reti
    """
    try:
        # Log dell'intero payload ricevuto
        payload = request.get_json()
        app.logger.info(f"Payload ricevuto da Splunk: {json.dumps(payload, indent=2)}")
        
        # Nome della ricerca che ha generato l'alert
        search_name = payload.get('search_name', '')
        
        # Splunk invia i risultati nella chiave 'results'
        if 'results' in payload:
            results = payload['results']
            
            for result in results:
                app.logger.info(f"Processando risultato: {result}")
                
                # Se l'alert è dalla ricerca dedicata alla policy di reputazione storica
                if search_name == 'TrustScoreReduction_AttackAttempts':
                    success = process_splunk_attack_alert(result)
                    if not success:
                        app.logger.error(f"Errore nel processare l'alert di attacco per: {result}")
                else:
                    # Gestione standard degli alert (codice esistente)
                    # Estrai IP dalla ricerca
                    ip_to_block = None
                    
                    # Controlla diversi possibili nomi di campo
                    for ip_field in ['src_ip', 'dst_ip', 'dest_ip', 'client_ip', 'ip']:
                        if ip_field in result:
                            ip_to_block = result[ip_field]
                            break
                    
                    if ip_to_block:
                        # Applica la policy di blocco
                        success = apply_block_policy(ip_to_block, result)
                        if success:
                            app.logger.info(f"Policy applicata con successo per IP: {ip_to_block}")
                        else:
                            app.logger.error(f"Errore nell'applicazione della policy per IP: {ip_to_block}")
                    else:
                        app.logger.warning(f"Nessun IP trovato nel risultato: {result}")
        
        return jsonify({"status": "success", "message": "Webhook processato"}), 200
        
    except Exception as e:
        app.logger.error(f"Errore nel processamento del webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/enforce', methods=['POST'])
def enforce_policy():
    """
    Endpoint legacy per compatibilità con script actions
    """
    try:
        data = request.get_json()
        app.logger.info(f"Richiesta enforcement ricevuta: {data}")
        
        ip = data.get('ip')
        action = data.get('action', 'block')
        
        if not ip:
            return jsonify({"error": "IP mancante"}), 400
        
        if action == 'block':
            success = apply_block_policy(ip, data)
            if success:
                return jsonify({"status": "blocked", "ip": ip}), 200
            else:
                return jsonify({"error": "Errore nel blocco"}), 500
        elif action == 'unblock':
            success = remove_block_policy(ip)
            if success:
                return jsonify({"status": "unblocked", "ip": ip}), 200
            else:
                return jsonify({"error": "Errore nella rimozione del blocco"}), 500
        
        return jsonify({"status": "action_not_supported"}), 400
        
    except Exception as e:
        app.logger.error(f"Errore nell'enforcement: {str(e)}")
        return jsonify({"error": str(e)}), 500

def run_iptables_command(cmd):
    """
    Esegue un comando iptables e restituisce il risultato
    """
    try:
        app.logger.debug(f"Eseguendo comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        app.logger.debug(f"Comando eseguito con successo: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Errore comando iptables: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        app.logger.error(f"Errore generico: {str(e)}")
        return False, str(e)

def apply_block_policy(ip, context_data=None):
    """
    Applica la policy di blocco per un determinato IP
    """
    try:
        app.logger.info(f"Tentativo di blocco IP: {ip}")
        
        # Verifica se la regola già esiste
        check_cmd = ["iptables", "-C", "FORWARD", "-s", ip, "-j", "DROP"]
        success, output = run_iptables_command(check_cmd)
        
        if success:
            app.logger.info(f"Regola per {ip} già esistente")
            return True
        
        # Aggiunge regola di blocco per traffico in uscita dall'IP
        block_cmd = ["iptables", "-I", "FORWARD", "1", "-s", ip, "-j", "DROP"]
        success, output = run_iptables_command(block_cmd)
        
        if success:
            app.logger.info(f"IP {ip} bloccato con successo (outbound)")
            
            # Aggiunge anche regola per traffico in entrata verso l'IP
            block_cmd_in = ["iptables", "-I", "FORWARD", "1", "-d", ip, "-j", "DROP"]
            success_in, output_in = run_iptables_command(block_cmd_in)
            
            if success_in:
                app.logger.info(f"IP {ip} bloccato con successo (inbound)")
            
            # Log additional context se disponibile
            if context_data:
                app.logger.info(f"Contesto alert: {json.dumps(context_data)}")
            
            return True
        else:
            app.logger.error(f"Errore nel blocco di {ip}: {output}")
            return False
        
    except Exception as e:
        app.logger.error(f"Errore nel blocco di {ip}: {str(e)}")
        return False

def remove_block_policy(ip):
    """
    Rimuove la policy di blocco per un determinato IP
    """
    try:
        app.logger.info(f"Tentativo di sblocco IP: {ip}")
        
        # Rimuove regola di blocco per traffico in uscita
        unblock_cmd = ["iptables", "-D", "FORWARD", "-s", ip, "-j", "DROP"]
        success1, output1 = run_iptables_command(unblock_cmd)
        
        # Rimuove regola di blocco per traffico in entrata
        unblock_cmd_in = ["iptables", "-D", "FORWARD", "-d", ip, "-j", "DROP"]
        success2, output2 = run_iptables_command(unblock_cmd_in)
        
        if success1 or success2:
            app.logger.info(f"IP {ip} sbloccato con successo")
            
            # Aggiorna anche il database se l'IP è nel sistema di fiducia
            try:
                conn = sqlite3.connect('/var/log/router/db/trust_scores.db')
                c = conn.cursor()
                c.execute('UPDATE trust_scores SET blocked = 0 WHERE ip = ?', (ip,))
                conn.commit()
                conn.close()
            except Exception as e:
                app.logger.warning(f"Errore nell'aggiornamento del DB per sblocco {ip}: {str(e)}")
                
            return True
        else:
            app.logger.warning(f"Nessuna regola trovata per {ip} o errore nella rimozione")
            return False
        
    except Exception as e:
        app.logger.error(f"Errore nello sblocco di {ip}: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

@app.route('/blocked-ips', methods=['GET'])
def list_blocked_ips():
    """
    Lista degli IP attualmente bloccati
    """
    try:
        blocked_ips = set()  # Usa set per evitare duplicati
        
        # Ottiene la lista delle regole iptables
        list_cmd = ["iptables", "-L", "FORWARD", "-n"]
        success, output = run_iptables_command(list_cmd)
        
        if success:
            lines = output.strip().split('\n')
            for line in lines:
                # Cerca righe con DROP che non siano per la porta 5432 (DB)
                if 'DROP' in line and 'dpt:5432' not in line:
                    parts = line.split()
                    # Format: DROP all -- * * source destination
                    if len(parts) >= 6:
                        source = parts[4]
                        dest = parts[5]
                        
                        # Estrai IP dal source (se non è 0.0.0.0/0)
                        if source != '0.0.0.0/0' and '.' in source:
                            ip = source.replace('/32', '')
                            if ip != '0.0.0.0':
                                blocked_ips.add(ip)
                        
                        # Estrai IP dal destination (se non è 0.0.0.0/0)
                        if dest != '0.0.0.0/0' and '.' in dest:
                            ip = dest.replace('/32', '')
                            if ip != '0.0.0.0':
                                blocked_ips.add(ip)
        
        # Converte set in lista ordinata
        blocked_ips_list = sorted(list(blocked_ips))
        return jsonify({"blocked_ips": blocked_ips_list, "count": len(blocked_ips_list)}), 200
        
    except Exception as e:
        app.logger.error(f"Errore nel recupero IP bloccati: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/iptables-rules', methods=['GET'])
def get_iptables_rules():
    """
    Mostra tutte le regole iptables attuali
    """
    try:
        list_cmd = ["iptables", "-L", "-n", "-v"]
        success, output = run_iptables_command(list_cmd)
        
        if success:
            return jsonify({"rules": output.split('\n')}), 200
        else:
            return jsonify({"error": "Errore nel recupero delle regole"}), 500
        
    except Exception as e:
        app.logger.error(f"Errore nel recupero regole iptables: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/trust-scores', methods=['GET'])
def view_trust_scores():
    """
    Endpoint per visualizzare i punteggi di fiducia di tutti gli IP
    """
    try:
        conn = sqlite3.connect('/var/log/router/db/trust_scores.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT ip, base_score, current_score, 
                   datetime(last_updated) as last_updated, 
                   blocked, block_reason, 
                   datetime(block_timestamp) as block_timestamp
            FROM trust_scores
            ORDER BY current_score ASC
        ''')
        
        scores = [dict(row) for row in c.fetchall()]
        
        c.execute('''
            SELECT ip, event_type, description, score_impact, 
                   datetime(timestamp) as timestamp
            FROM security_events
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        
        events = [dict(row) for row in c.fetchall()]
        
        conn.close()
        
        return jsonify({
            "trust_scores": scores,
            "recent_events": events
        }), 200
        
    except Exception as e:
        app.logger.error(f"Errore nel recupero dei punteggi di fiducia: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Inizializza il database dei punteggi di fiducia
    init_trust_db()
    # Avvia l'app Flask
    app.run(host='0.0.0.0', port=5000, debug=True)