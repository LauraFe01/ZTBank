import ipaddress
from .base_dao import BaseDAO

class UtentiIpDAO(BaseDAO):
    """DAO per gestione associazioni utenti-IP"""
    
    VALID_IP_ROLES = {'internal', 'external', 'wifi'}

    def create(self, utente_id, ip_address, ip_ruolo):
        if ip_ruolo not in self.VALID_IP_ROLES:
            raise ValueError(f"ip_ruolo non valido: {ip_ruolo}")
        
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise ValueError(f"Indirizzo IP non valido: {ip_address}")
        
        query = "INSERT INTO utenti_ip (utente_id, ip_address, ip_ruolo) VALUES (%s, %s, %s) RETURNING *"
        return self._execute_query(query, (utente_id, ip_address, ip_ruolo), fetch_one=True)

    def read(self, id):
        query = "SELECT * FROM utenti_ip WHERE id = %s"
        return self._execute_query(query, (id,), fetch_one=True)

    def read_all(self):
        query = "SELECT * FROM utenti_ip"
        return self._execute_query(query, fetch_all=True)

    def read_by_user(self, utente_id):
        query = "SELECT * FROM utenti_ip WHERE utente_id = %s"
        return self._execute_query(query, (utente_id,), fetch_all=True)

    def read_by_ip(self, ip_address):
        query = "SELECT * FROM utenti_ip WHERE ip_address = %s"
        return self._execute_query(query, (ip_address,), fetch_all=True)

    def update(self, id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        
        set_clause = ', '.join(f"{k} = %s" for k in fields)
        query = f"UPDATE utenti_ip SET {set_clause} WHERE id = %s RETURNING *"
        params = list(fields.values()) + [id]
        return self._execute_query(query, tuple(params), fetch_one=True)

    def delete(self, id):
        query = "DELETE FROM utenti_ip WHERE id = %s"
        return self._execute_query(query, (id,))
