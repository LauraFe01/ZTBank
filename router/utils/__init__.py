"""
Utils package per il sistema Zero Trust Bancario

Questo package fornisce tutti gli strumenti necessari per il funzionamento
del sistema Zero Trust, organizzati in moduli specializzati.

Struttura:
- database/: Gestione connessioni e configurazione database
- dao/: Data Access Objects per operazioni CRUD su ogni tabella
- repository/: Pattern Repository per accesso centralizzato ai dati
- managers/: Managers di alto livello per logica business specifica
- services/: Servizi per logiche business complesse

Compatibilità:
Espone direttamente db_manager e iptables_manager per mantenere
la compatibilità con il codice esistente (es. policy_1.py).
"""

from .managers.db_manager import db_manager
from .managers.iptables_manager import iptables_manager

# Esporta i manager principali per compatibilità con policy_1.py
__all__ = [
    'db_manager',
    'iptables_manager'
]

# Versione del package utils
__version__ = '1.0.0'