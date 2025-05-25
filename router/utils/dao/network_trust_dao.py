from .base_dao import BaseDAO
from typing import Optional, List, Dict

class NetworkTrustDAO(BaseDAO):
    """DAO per gestione network trust - Policy 1"""

    def reduce_trust(self, ip_address: str, reduction: int, reason: str, attack_count: int) -> bool:
        """Riduce il trust score usando la funzione PostgreSQL"""
        query = "SELECT update_network_trust(%s, %s, %s, %s)"
        try:
            self._execute_query(query, (ip_address, reduction, reason, attack_count))
            return True
        except Exception:
            return False

    def get_trust_info(self, ip_address: str) -> Optional[Dict]:
        """Ottiene informazioni sul trust di un IP"""
        query = """SELECT ip_address, initial_trust_score, current_trust_score, 
                          attack_count, last_attack_time, is_blocked, notes
                   FROM network_trust WHERE ip_address = %s"""
        
        result = self._execute_query(query, (ip_address,), fetch_one=True)
        if result:
            return {
                'ip_address': str(result[0]),
                'initial_trust_score': result[1],
                'current_trust_score': result[2],
                'attack_count': result[3],
                'last_attack_time': result[4],
                'is_blocked': result[5],
                'notes': result[6]
            }
        return None

    def get_blocked_ips(self) -> List[str]:
        """Ottiene lista IP bloccati"""
        query = "SELECT ip_address FROM network_trust WHERE is_blocked = TRUE OR current_trust_score <= 20"
        results = self._execute_query(query, fetch_all=True)
        return [str(row[0]) for row in results]

    def get_reduction_history(self, ip_address: str = None) -> List[Dict]:
        """Ottiene storico riduzioni trust"""
        if ip_address:
            query = """SELECT ip_address, reduction_amount, reason, attack_count, timestamp
                      FROM trust_reduction_log WHERE ip_address = %s ORDER BY timestamp DESC"""
            results = self._execute_query(query, (ip_address,), fetch_all=True)
        else:
            query = """SELECT ip_address, reduction_amount, reason, attack_count, timestamp
                      FROM trust_reduction_log ORDER BY timestamp DESC LIMIT 100"""
            results = self._execute_query(query, fetch_all=True)

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

    def get_all_network_trust(self) -> List[Dict]:
        """Ottiene tutti i record di network trust"""
        query = """SELECT ip_address, initial_trust_score, current_trust_score, 
                          attack_count, last_attack_time, is_blocked
                   FROM network_trust ORDER BY current_trust_score ASC"""
        
        results = self._execute_query(query, fetch_all=True)
        return [
            {
                'ip_address': str(row[0]),
                'initial_trust_score': row[1],
                'current_trust_score': row[2],
                'attack_count': row[3],
                'last_attack_time': row[4],
                'is_blocked': row[5]
            }
            for row in results
        ]