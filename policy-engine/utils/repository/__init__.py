"""
Repository Pattern - Accesso centralizzato ai dati

Il Repository fornisce un'interfaccia unificata per accedere a tutti i DAO,
implementando il pattern Repository per:
- Centralizzare la logica di accesso ai dati
- Gestire le connessioni database in modo efficiente
- Fornire un'API pulita per i servizi di livello superiore

Utilizzo:
    from utils.repository.repository import Repository
    
    repo = Repository()
    user = repo.users.read_by_username("cliente1")
    trust_info = repo.network_trust.get_trust_info("192.168.1.100")
    repo.close()
"""

from .repository import Repository

__all__ = [
    'Repository'
]