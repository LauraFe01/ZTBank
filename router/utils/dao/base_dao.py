import psycopg2
from abc import ABC, abstractmethod

class BaseDAO(ABC):
    """Classe base per tutti i DAO"""
    
    def __init__(self, connection):
        self.conn = connection
    
    def _execute_query(self, query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = False):
        """Esegue una query con gestione errori centralizzata"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                
                self.conn.commit()
                return cursor.rowcount
                
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore database: {e}")