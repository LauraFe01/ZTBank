import psycopg2
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Gestisce la connessione al database PostgreSQL"""
    
    def __init__(self, config: dict):
        self.config = config
        self._connection = None
    
    def connect(self) -> psycopg2.extensions.connection:
        """Crea e restituisce una connessione al database"""
        try:
            if self._connection is None or self._connection.closed:
                self._connection = psycopg2.connect(**self.config)
            return self._connection
        except Exception as e:
            logger.error(f"Errore connessione database: {e}")
            raise
    
    def close(self):
        """Chiude la connessione al database"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None