"""
Policy 1 Handler: Riduzione automatica della fiducia delle reti
- Le reti con più di 10 tentativi di attacco negli ultimi 30 giorni ricevono una riduzione automatica della fiducia di 25-30 punti
"""

import logging
from flask import jsonify, current_app
from utils.db import db_manager
from utils.iptables import iptables_manager

logger = logging.getLogger("policy 1")

def handle(data):
    """
    Gestisce la Policy 1: riduzione trust score per reti con tentativi di attacco
    
    Args:
        data: Payload JSON da Splunk con i risultati della saved search
    
    Returns:
        Flask response JSON
    """
    try:
        current_app.logger.info("=== POLICY 1: Gestione riduzione trust score ===")
        current_app.logger.info(f"Payload ricevuto: {data}")
        
        # Estrai i risultati dalla saved search
        results = data.get('result', {})
        
        # Se non ci sono risultati, exit
        if not results:
            current_app.logger.info("Nessun risultato da processare")
            return jsonify({"status": "success", "message": "Nessun IP da processare"}), 200
        
        processed_ips = []
        
        # Processa ogni IP nei risultati
        if isinstance(results, list):
            ip_list = results
        else:
            # Se è un singolo risultato, convertilo in lista
            ip_list = [results]
        
        for result in ip_list:
            try:
                # Estrai informazioni dal risultato
                src_ip = result.get('src_ip')
                attack_count = int(result.get('count', 0))
                trust_reduction = int(result.get('trust_reduction', 25))
                reason = result.get('reason', 'Multiple attack attempts in last 30 days')
                
                if not src_ip:
                    current_app.logger.warning("IP sorgente mancante nel risultato")
                    continue
                
                current_app.logger.info(f"Processando IP: {src_ip}, Attacchi: {attack_count}, Riduzione: {trust_reduction}")
                
                # 1. Aggiorna database con riduzione trust score
                db_success = db_manager.reduce_network_trust(
                    ip_address=src_ip,
                    reduction=trust_reduction,
                    reason=reason,
                    attack_count=attack_count
                )
                
                if not db_success:
                    current_app.logger.error(f"Errore durante aggiornamento database per IP {src_ip}")
                    continue
                
                # 2. Ottieni il nuovo trust score per applicare le regole appropriate
                trust_info = db_manager.get_network_trust(src_ip)
                if trust_info:
                    current_trust = trust_info['current_trust_score']
                    current_app.logger.info(f"Nuovo trust score per IP {src_ip}: {current_trust}")
                    
                    # 3. Applica regole IPTables basate sul trust score
                    iptables_success = iptables_manager.apply_trust_based_rules(src_ip, current_trust)
                    
                    if iptables_success:
                        processed_ips.append({
                            'ip': src_ip,
                            'old_trust': 100,  # Assumiamo 100 come default iniziale
                            'new_trust': current_trust,
                            'reduction': trust_reduction,
                            'attack_count': attack_count,
                            'action_taken': get_action_description(current_trust)
                        })
                        current_app.logger.info(f"IP {src_ip} processato con successo")
                    else:
                        current_app.logger.error(f"Errore durante applicazione regole IPTables per IP {src_ip}")
                else:
                    current_app.logger.error(f"Impossibile ottenere trust info per IP {src_ip}")
                
            except Exception as e:
                current_app.logger.error(f"Errore durante processing singolo IP: {e}")
                continue
        
        # Prepara risposta
        if processed_ips:
            response_data = {
                "status": "success",
                "message": f"Policy 1 applicata a {len(processed_ips)} IP",
                "processed_ips": processed_ips,
                "timestamp": data.get('timestamp', 'N/A')
            }
            current_app.logger.info(f"Policy 1 completata con successo: {len(processed_ips)} IP processati")
        else:
            response_data = {
                "status": "warning",
                "message": "Nessun IP processato con successo",
                "timestamp": data.get('timestamp', 'N/A')
            }
            current_app.logger.warning("Policy 1 completata ma nessun IP processato")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Errore durante gestione Policy 1: {e}")
        return jsonify({
            "status": "error",
            "message": f"Errore durante processing Policy 1: {str(e)}"
        }), 500

def get_action_description(trust_score):
    """
    Restituisce descrizione dell'azione intrapresa basata sul trust score
    """
    if trust_score <= 20:
        return "IP bloccato completamente"
    elif trust_score <= 40:
        return "Banda limitata a 50 kbps"
    elif trust_score <= 60:
        return "Banda limitata a 200 kbps"
    else:
        return "Nessuna restrizione aggiuntiva"

