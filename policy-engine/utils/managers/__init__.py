"""
Managers - Logica business di alto livello

I manager implementano logiche business specifiche combinando
l'accesso ai dati tramite Repository con operazioni esterne:

- DatabaseManager: Operazioni database per le policy (compatibile con policy_1.py)
- IPTablesManager: Gestione regole firewall IPTables (compatibile con policy_1.py)

Questi manager mantengono la compatibilità con il codice esistente
fornendo le stesse interfacce pubbliche ma con implementazione migliorata.

Utilizzo:
    from utils.managers.db_manager import db_manager
    from utils.managers.iptables_manager import iptables_manager
    
    # Uso identico al codice precedente
    success = db_manager.reduce_network_trust(ip, reduction, reason, count)
    iptables_manager.apply_trust_based_rules(ip, trust_score)
"""

from .db_manager import DatabaseManager, db_manager
from .iptables_manager import IPTablesManager, iptables_manager

__all__ = [
    'DatabaseManager',
    'db_manager',
    'IPTablesManager', 
    'iptables_manager'
]