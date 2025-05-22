import re
import psycopg2

class UserDAO:
    VALID_ROLES = {'direttore', 'cassiere', 'consulente', 'cliente'}

    def __init__(self, conn):
        self.conn = conn

    def create(self, username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score):
        # Validazione ruolo
        if ruolo not in self.VALID_ROLES:
            raise ValueError(f"Ruolo non valido: {ruolo}")
        # Validazione email semplice
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError(f"Email non valida: {email}")
        # Validazione campi obbligatori
        if not username or not codice_fiscale:
            raise ValueError("Username e codice fiscale sono obbligatori")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO utenti (username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *",
                    (username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score)
                )
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in create user: {e}")

    def read(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti WHERE id = %s", (user_id,))
                return cur.fetchone()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read user: {e}")

    def read_all(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti")
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_all users: {e}")

    def read_by_username(self, username):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM utenti WHERE username = %s", (username,))
                return cur.fetchone()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_by_username: {e}")

    def update(self, user_id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        keys = ', '.join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [user_id]
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE utenti SET {keys} WHERE id = %s RETURNING *", values)
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in update user: {e}")

    def delete(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM utenti WHERE id = %s", (user_id,))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in delete user: {e}")