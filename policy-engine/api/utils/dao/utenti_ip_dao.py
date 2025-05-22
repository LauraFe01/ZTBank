import ipaddress
import psycopg2

class UtentiIpDAO:
    VALID_IP_ROLES = {'internal', 'external', 'wifi'}

    def __init__(self, conn):
        self.conn = conn

    def create(self, utente_id, ip_address, ip_ruolo):
        # Validazione ruolo IP
        if ip_ruolo not in self.VALID_IP_ROLES:
            raise ValueError(f"ip_ruolo non valido: {ip_ruolo}")
        # Validazione indirizzo IP
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise ValueError(f"Indirizzo IP non valido: {ip_address}")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO utenti_ip (utente_id, ip_address, ip_ruolo) VALUES (%s, %s, %s) RETURNING *",
                    (utente_id, ip_address, ip_ruolo)
                )
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in create utenti_ip: {e}")

    def read(self, id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti_ip WHERE id = %s", (id,))
                return cur.fetchone()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read utenti_ip: {e}")

    def read_all(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti_ip")
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_all utenti_ip: {e}")

    def read_by_user(self, utente_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti_ip WHERE utente_id = %s", (utente_id,))
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_by_user utenti_ip: {e}")

    def read_by_ip(self, ip_address):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti_ip WHERE ip_address = %s", (ip_address,))
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_by_ip utenti_ip: {e}")

    def update(self, id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        keys = ', '.join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [id]
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE utenti_ip SET {keys} WHERE id = %s RETURNING *", values)
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in update utenti_ip: {e}")

    def delete(self, id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM utenti_ip WHERE id = %s", (id,))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in delete utenti_ip: {e}")