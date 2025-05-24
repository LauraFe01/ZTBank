import psycopg2
import logging
from datetime import datetime
from typing import Optional, Dict, List
from flask import current_app

# Configurazione database
DB_CONFIG = {
    'host': '192.168.200.10',
    'database': 'mydb',
    'user': 'myuser',
    'password': 'mypass',
    'port': 5432
}

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        """Crea connessione al database"""
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            current_app.logger.error(f"Errore connessione database: {e}")
            raise
    
    def reduce_network_trust(self, ip_address: str, reduction: int, reason: str, attack_count: int) -> bool:
        """
        Riduce il trust score di una rete/IP
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Chiama la funzione PostgreSQL per aggiornare il trust
                    cursor.execute("""
                        SELECT update_network_trust(%s, %s, %s, %s)
                    """, (ip_address, reduction, reason, attack_count))
                    
                    conn.commit()
                    current_app.logger.info(f"Trust score ridotto per IP {ip_address}: -{reduction} punti. Motivo: {reason}")
                    return True
                    
        except Exception as e:
            current_app.logger.error(f"Errore durante riduzione trust score per IP {ip_address}: {e}")
            return False
    
    def get_network_trust(self, ip_address: str) -> Optional[Dict]:
        """
        Ottiene informazioni sul trust score di un IP
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT ip_address, initial_trust_score, current_trust_score, 
                               attack_count, last_attack_time, is_blocked
                        FROM network_trust 
                        WHERE ip_address = %s
                    """, (ip_address,))
                    
                    result = cursor.fetchone()
                    if result:
                        return {
                            'ip_address': str(result[0]),
                            'initial_trust_score': result[1],
                            'current_trust_score': result[2],
                            'attack_count': result[3],
                            'last_attack_time': result[4],
                            'is_blocked': result[5]
                        }
                    return None
                    
        except Exception as e:
            current_app.logger.error(f"Errore durante lettura trust score per IP {ip_address}: {e}")
            return None
    
    def get_blocked_ips(self) -> List[str]:
        """
        Ottiene lista degli IP bloccati (trust score <= 20)
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT ip_address 
                        FROM network_trust 
                        WHERE is_blocked = TRUE OR current_trust_score <= 20
                    """)
                    
                    results = cursor.fetchall()
                    return [str(row[0]) for row in results]
                    
        except Exception as e:
            current_app.logger.error(f"Errore durante lettura IP bloccati: {e}")
            return []
    
    def get_trust_reduction_history(self, ip_address: str = None) -> List[Dict]:
        """
        Ottiene storico riduzioni trust score
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if ip_address:
                        cursor.execute("""
                            SELECT ip_address, reduction_amount, reason, attack_count, timestamp
                            FROM trust_reduction_log 
                            WHERE ip_address = %s
                            ORDER BY timestamp DESC
                        """, (ip_address,))
                    else:
                        cursor.execute("""
                            SELECT ip_address, reduction_amount, reason, attack_count, timestamp
                            FROM trust_reduction_log 
                            ORDER BY timestamp DESC
                            LIMIT 100
                        """)
                    
                    results = cursor.fetchall()
                    return [
                        {
                            'ip_address': str(row[0]),
                            'reduction_amount': row[1],
                            'reason': row[2],
                            'attack_count': row[3],
                            'timestamp': row[4]
                        }
                        for row in results
                    ]
                    
        except Exception as e:
            current_app.logger.error(f"Errore durante lettura storico trust reduction: {e}")
            return []

# Istanza globale
db_manager = DatabaseManager()