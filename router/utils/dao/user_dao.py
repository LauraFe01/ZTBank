import re
from .base_dao import BaseDAO

class UserDAO(BaseDAO):
    """DAO per gestione utenti"""
    
    VALID_ROLES = {'direttore', 'cassiere', 'consulente', 'cliente'}

    def create(self, username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score=None):
        if ruolo not in self.VALID_ROLES:
            raise ValueError(f"Ruolo non valido: {ruolo}")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError(f"Email non valida: {email}")
        if not username or not codice_fiscale:
            raise ValueError("Username e codice fiscale sono obbligatori")
        
        query = """INSERT INTO utenti (username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *"""
        return self._execute_query(query, (username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score), fetch_one=True)

    def read(self, user_id):
        query = "SELECT * FROM utenti WHERE id = %s"
        return self._execute_query(query, (user_id,), fetch_one=True)

    def read_by_username(self, username):
        query = "SELECT * FROM utenti WHERE username = %s"
        return self._execute_query(query, (username,), fetch_one=True)

    def read_all(self):
        query = "SELECT * FROM utenti"
        return self._execute_query(query, fetch_all=True)

    def update(self, user_id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        
        set_clause = ', '.join(f"{k} = %s" for k in fields)
        query = f"UPDATE utenti SET {set_clause} WHERE id = %s RETURNING *"
        params = list(fields.values()) + [user_id]
        return self._execute_query(query, tuple(params), fetch_one=True)

    def delete(self, user_id):
        query = "DELETE FROM utenti WHERE id = %s"
        return self._execute_query(query, (user_id,))