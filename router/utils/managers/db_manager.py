import logging
from typing import Optional, Dict, List
from utils.repository.repository import Repository

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manager per operazioni database - Compatibile con policy_1.py"""
    
    def __init__(self):
        self.repository = Repository()
    
    def reduce_network_trust(self, ip_address: str, reduction: int, reason: str, attack_count: int) -> bool:
        """Riduce il trust score di una rete/IP - USATO DA POLICY_1"""
        try:
            return self.repository.network_trust.reduce_trust(ip_address, reduction, reason, attack_count)
        except Exception as e:
            logger.error(f"Errore durante riduzione trust score per IP {ip_address}: {e}")
            return False
    
    def get_network_trust(self, ip_address: str) -> Optional[Dict]:
        """Ottiene informazioni sul trust score di un IP - USATO DA POLICY_1"""
        try:
            return self.repository.network_trust.get_trust_info(ip_address)
        except Exception as e:
            logger.error(f"Errore durante lettura trust score per IP {ip_address}: {e}")
            return None
    
    def get_blocked_ips(self) -> List[str]:
        """Ottiene lista degli IP bloccati"""
        try:
            return self.repository.network_trust.get_blocked_ips()
        except Exception as e:
            logger.error(f"Errore durante lettura IP bloccati: {e}")
            return []
    
    def get_trust_reduction_history(self, ip_address: str = None) -> List[Dict]:
        """Ottiene storico riduzioni trust score"""
        try:
            return self.repository.network_trust.get_reduction_history(ip_address)
        except Exception as e:
            logger.error(f"Errore durante lettura storico trust reduction: {e}")
            return []

# Istanza globale per compatibilità con policy_1.py
db_manager = DatabaseManager()