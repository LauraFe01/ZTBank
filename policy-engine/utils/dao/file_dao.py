from .base_dao import BaseDAO

class FileDAO(BaseDAO):
    """DAO per gestione file e documenti"""
    
    VALID_SENSIBILITA = {'sensibile', 'non_sensibile'}

    def create(self, nome_file, contenuto, sensibilita, proprietario_id):
        if sensibilita not in self.VALID_SENSIBILITA:
            raise ValueError(f"Sensibilità non valida: {sensibilita}")
        if not nome_file:
            raise ValueError("Il nome del file è obbligatorio")
        
        query = """INSERT INTO file_documenti (nome_file, contenuto, sensibilita, proprietario_id) 
                   VALUES (%s, %s, %s, %s) RETURNING *"""
        return self._execute_query(query, (nome_file, contenuto, sensibilita, proprietario_id), fetch_one=True)

    def read(self, file_id):
        query = "SELECT * FROM file_documenti WHERE id = %s"
        return self._execute_query(query, (file_id,), fetch_one=True)

    def read_all(self):
        query = "SELECT * FROM file_documenti"
        return self._execute_query(query, fetch_all=True)

    def read_by_owner(self, proprietario_id):
        query = "SELECT * FROM file_documenti WHERE proprietario_id = %s"
        return self._execute_query(query, (proprietario_id,), fetch_all=True)

    def read_by_sensitivity(self, sensibilita):
        if sensibilita not in self.VALID_SENSIBILITA:
            raise ValueError(f"Sensibilità non valida: {sensibilita}")
        
        query = "SELECT * FROM file_documenti WHERE sensibilita = %s"
        return self._execute_query(query, (sensibilita,), fetch_all=True)

    def update(self, file_id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        
        set_clause = ', '.join(f"{k} = %s" for k in fields)
        query = f"UPDATE file_documenti SET {set_clause} WHERE id = %s RETURNING *"
        params = list(fields.values()) + [file_id]
        return self._execute_query(query, tuple(params), fetch_one=True)

    def delete(self, file_id):
        query = "DELETE FROM file_documenti WHERE id = %s"
        return self._execute_query(query, (file_id,))