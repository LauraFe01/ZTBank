from .base_dao import BaseDAO

class AccessLogDAO(BaseDAO):
    """DAO per gestione log degli accessi"""
    
    VALID_AZIONI = {'lettura', 'scrittura', 'cancellazione'}

    def create(self, utente_id, file_id, azione, esito, motivazione):
        if azione not in self.VALID_AZIONI:
            raise ValueError(f"Azione non valida: {azione}")
        if not isinstance(esito, bool):
            raise ValueError("Esito deve essere booleano")
        
        query = """INSERT INTO access_log (utente_id, file_id, azione, esito, motivazione) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING *"""
        return self._execute_query(query, (utente_id, file_id, azione, esito, motivazione), fetch_one=True)

    def read(self, log_id):
        query = "SELECT * FROM access_log WHERE id = %s"
        return self._execute_query(query, (log_id,), fetch_one=True)

    def read_all(self):
        query = "SELECT * FROM access_log ORDER BY timestamp DESC"
        return self._execute_query(query, fetch_all=True)

    def read_by_user(self, utente_id):
        query = "SELECT * FROM access_log WHERE utente_id = %s ORDER BY timestamp DESC"
        return self._execute_query(query, (utente_id,), fetch_all=True)

    def read_by_file(self, file_id):
        query = "SELECT * FROM access_log WHERE file_id = %s ORDER BY timestamp DESC"
        return self._execute_query(query, (file_id,), fetch_all=True)

    def read_by_action(self, azione):
        if azione not in self.VALID_AZIONI:
            raise ValueError(f"Azione non valida: {azione}")
        
        query = "SELECT * FROM access_log WHERE azione = %s ORDER BY timestamp DESC"
        return self._execute_query(query, (azione,), fetch_all=True)

    def read_by_outcome(self, esito):
        if not isinstance(esito, bool):
            raise ValueError("Esito deve essere booleano")
        
        query = "SELECT * FROM access_log WHERE esito = %s ORDER BY timestamp DESC"
        return self._execute_query(query, (esito,), fetch_all=True)

    def update(self, log_id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        
        set_clause = ', '.join(f"{k} = %s" for k in fields)
        query = f"UPDATE access_log SET {set_clause} WHERE id = %s RETURNING *"
        params = list(fields.values()) + [log_id]
        return self._execute_query(query, tuple(params), fetch_one=True)

    def delete(self, log_id):
        query = "DELETE FROM access_log WHERE id = %s"
        return self._execute_query(query, (log_id,))