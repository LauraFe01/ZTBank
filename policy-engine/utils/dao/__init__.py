"""
Data Access Objects (DAO) - Operazioni CRUD per ogni tabella

Ogni DAO gestisce le operazioni database per una specifica tabella:
- BaseDAO: Classe base con funzionalità comuni e gestione errori
- UserDAO: Gestione tabella utenti
- UtentiIpDAO: Gestione associazioni utenti-IP
- FileDAO: Gestione file e documenti
- AccessLogDAO: Gestione log degli accessi
- NetworkTrustDAO: Gestione trust delle reti (Policy 1)

Pattern utilizzato:
- Ereditarietà da BaseDAO per funzionalità comuni
- Validazione input specifica per ogni entità
- Gestione errori centralizzata
- Query parametrizzate per sicurezza

Utilizzo:
    from utils.dao import UserDAO
    
    user_dao = UserDAO(connection)
    user = user_dao.read_by_username("cliente1")
"""

from .base_dao import BaseDAO
from .user_dao import UserDAO
from .utenti_ip_dao import UtentiIpDAO
from .file_dao import FileDAO
from .access_log_dao import AccessLogDAO
from .network_trust_dao import NetworkTrustDAO

__all__ = [
    'BaseDAO',
    'UserDAO',
    'UtentiIpDAO', 
    'FileDAO',
    'AccessLogDAO',
    'NetworkTrustDAO'
]