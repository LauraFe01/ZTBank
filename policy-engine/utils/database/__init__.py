"""
Database package - Gestione connessioni e configurazione

Fornisce:
- DatabaseConnection: Classe per gestire connessioni PostgreSQL
- DB_CONFIG: Configurazione centralizzata del database

Utilizzo:
    from utils.database.connection import DatabaseConnection
    from utils.database.config import DB_CONFIG
    
    db = DatabaseConnection(DB_CONFIG)
    conn = db.connect()
"""

from .connection import DatabaseConnection
from .config import DB_CONFIG

__all__ = [
    'DatabaseConnection',
    'DB_CONFIG'
]