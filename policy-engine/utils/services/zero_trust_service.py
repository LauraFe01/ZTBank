from typing import Dict, List, Optional
from utils.repository.repository import Repository
import logging

logger = logging.getLogger(__name__)

class ZeroTrustService:
    """Servizio per logiche business Zero Trust"""
    
    def __init__(self):
        self.repository = Repository()
    
    def evaluate_user_access(self, username: str, file_id: int, action: str) -> Dict:
        """
        Valuta se un utente può accedere a una risorsa
        
        Returns:
            Dict con risultato della valutazione
        """
        try:
            # Ottieni informazioni utente
            user = self.repository.users.read_by_username(username)
            if not user:
                return {"allowed": False, "reason": "Utente non trovato"}
            
            # Ottieni informazioni file
            file_info = self.repository.files.read(file_id)
            if not file_info:
                return {"allowed": False, "reason": "File non trovato"}
            
            # Logica di valutazione trust score
            user_trust = user[7]  # trust_score è il campo 7
            file_sensitivity = file_info[3]  # sensibilita è il campo 3
            
            # Soglie basate su sensibilità e azione
            required_trust = self._get_required_trust(file_sensitivity, action)
            
            allowed = user_trust >= required_trust
            
            # Log dell'accesso
            self.repository.access_logs.create(
                utente_id=user[0],
                file_id=file_id,
                azione=action,
                esito=allowed,
                motivazione=f"Trust: {user_trust}, Richiesto: {required_trust}"
            )
            
            return {
                "allowed": allowed,
                "user_trust": user_trust,
                "required_trust": required_trust,
                "reason": "Accesso consentito" if allowed else f"Trust insufficiente: {user_trust} < {required_trust}"
            }
            
        except Exception as e:
            logger.error(f"Errore durante valutazione accesso: {e}")
            return {"allowed": False, "reason": "Errore interno"}
    
    def _get_required_trust(self, sensitivity: str, action: str) -> int:
        """Calcola trust richiesto basato su sensibilità e azione"""
        base_requirements = {
            'sensibile': {'lettura': 65, 'scrittura': 80, 'cancellazione': 85},
            'non_sensibile': {'lettura': 60, 'scrittura': 70, 'cancellazione': 75}
        }
        
        return base_requirements.get(sensitivity, {}).get(action, 100)
    
    def get_network_security_report(self) -> Dict:
        """Genera report sicurezza di rete"""
        try:
            all_trust = self.repository.network_trust.get_all_network_trust()
            blocked_ips = self.repository.network_trust.get_blocked_ips()
            recent_reductions = self.repository.network_trust.get_reduction_history()[:10]
            
            # Statistiche
            total_ips = len(all_trust)
            high_trust = len([ip for ip in all_trust if ip['current_trust_score'] > 80])
            medium_trust = len([ip for ip in all_trust if 60 < ip['current_trust_score'] <= 80])
            low_trust = len([ip for ip in all_trust if 20 < ip['current_trust_score'] <= 60])
            blocked = len(blocked_ips)
            
            return {
                "summary": {
                    "total_ips": total_ips,
                    "high_trust_ips": high_trust,
                    "medium_trust_ips": medium_trust,
                    "low_trust_ips": low_trust,
                    "blocked_ips": blocked
                },
                "blocked_ips": blocked_ips,
                "recent_trust_reductions": recent_reductions,
                "trust_distribution": {
                    "high": high_trust,
                    "medium": medium_trust,
                    "low": low_trust,
                    "blocked": blocked
                }
            }
            
        except Exception as e:
            logger.error(f"Errore durante generazione report: {e}")
            return {"error": "Errore durante generazione report"}
