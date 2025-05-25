import subprocess
import logging
from typing import List

logger = logging.getLogger(__name__)

class IPTablesManager:
    """Manager per gestione regole IPTables - Compatibile con policy_1.py"""
    
    def __init__(self):
        self.chain_name = "ZERO_TRUST_POLICY"
        self.setup_chain()
    
    def setup_chain(self):
        """Inizializza la catena IPTables per le policy Zero Trust"""
        try:
            # Crea catena personalizzata se non esiste
            subprocess.run([
                "iptables", "-t", "filter", "-N", self.chain_name
            ], capture_output=True, check=False)
            
            # Verifica se la regola di jump esiste già
            result = subprocess.run([
                "iptables", "-t", "filter", "-C", "INPUT", "-j", self.chain_name
            ], capture_output=True, check=False)
            
            # Se non esiste, aggiungila
            if result.returncode != 0:
                subprocess.run([
                    "iptables", "-t", "filter", "-I", "INPUT", "1", "-j", self.chain_name
                ], check=True)
            
            logger.info(f"Catena IPTables {self.chain_name} inizializzata")
            
        except Exception as e:
            logger.error(f"Errore durante setup catena IPTables: {e}")
    
    def block_ip(self, ip_address: str, reason: str = "Trust score ridotto") -> bool:
        """Blocca un IP aggiungendo regola IPTables"""
        try:
            # Verifica se la regola esiste già
            check_result = subprocess.run([
                "iptables", "-t", "filter", "-C", self.chain_name, 
                "-s", ip_address, "-j", "DROP"
            ], capture_output=True, check=False)
            
            if check_result.returncode == 0:
                logger.info(f"IP {ip_address} già bloccato")
                return True
            
            # Aggiungi regola di blocco
            subprocess.run([
                "iptables", "-t", "filter", "-A", self.chain_name,
                "-s", ip_address, "-j", "DROP",
                "-m", "comment", "--comment", f"BLOCKED: {reason}"
            ], check=True)
            
            logger.info(f"IP {ip_address} bloccato via IPTables. Motivo: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Errore durante blocco IP {ip_address}: {e}")
            return False
    
    def limit_ip_bandwidth(self, ip_address: str, limit_kbps: int = 100) -> bool:
        """Limita la banda per un IP con trust score basso"""
        try:
            # Verifica se la regola esiste già
            check_result = subprocess.run([
                "iptables", "-t", "filter", "-C", self.chain_name,
                "-s", ip_address, "-m", "limit", "--limit", f"{limit_kbps}/sec"
            ], capture_output=True, check=False)
            
            if check_result.returncode == 0:
                logger.info(f"Limite banda per IP {ip_address} già attivo")
                return True
            
            # Aggiungi limite di banda
            subprocess.run([
                "iptables", "-t", "filter", "-A", self.chain_name,
                "-s", ip_address, "-m", "limit", "--limit", f"{limit_kbps}/sec",
                "-j", "ACCEPT", "-m", "comment", 
                "--comment", f"BANDWIDTH_LIMITED: {limit_kbps}kbps"
            ], check=True)
            
            logger.info(f"Limite banda applicato a IP {ip_address}: {limit_kbps} kbps")
            return True
            
        except Exception as e:
            logger.error(f"Errore durante limitazione banda IP {ip_address}: {e}")
            return False
    
    def apply_trust_based_rules(self, ip_address: str, trust_score: int) -> bool:
        """Applica regole basate sul trust score - USATO DA POLICY_1"""
        try:
            if trust_score <= 20:
                # Trust score molto basso: blocca completamente
                return self.block_ip(ip_address, f"Trust score troppo basso: {trust_score}")
            
            elif trust_score <= 40:
                # Trust score basso: limita banda drasticamente
                return self.limit_ip_bandwidth(ip_address, 50)
            
            elif trust_score <= 60:
                # Trust score medio-basso: limita banda moderatamente
                return self.limit_ip_bandwidth(ip_address, 200)
            
            else:
                # Trust score accettabile: nessuna restrizione aggiuntiva
                logger.info(f"IP {ip_address} con trust score {trust_score}: nessuna restrizione")
                return True
                
        except Exception as e:
            logger.error(f"Errore durante applicazione regole trust-based per IP {ip_address}: {e}")
            return False

# Istanza globale per compatibilità con policy_1.py
iptables_manager = IPTablesManager()