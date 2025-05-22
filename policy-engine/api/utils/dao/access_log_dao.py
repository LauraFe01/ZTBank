import psycopg2

class AccessLogDAO:
    VALID_AZIONI = {'lettura', 'scrittura', 'cancellazione'}

    def __init__(self, conn):
        self.conn = conn

    def create(self, utente_id, file_id, azione, esito, motivazione):
        # Validazione azione
        if azione not in self.VALID_AZIONI:
            raise ValueError(f"Azione non valida: {azione}")
        # Validazione esito booleano
        if not isinstance(esito, bool):
            raise ValueError("Esito deve essere booleano")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO access_log (utente_id, file_id, azione, esito, motivazione) VALUES (%s, %s, %s, %s, %s) RETURNING *",
                    (utente_id, file_id, azione, esito, motivazione)
                )
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in create access_log: {e}")

    def read(self, log_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM access_log WHERE id = %s", (log_id,))
                return cur.fetchone()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read access_log: {e}")

    def read_all(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM access_log")
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_all access_log: {e}")

    def read_by_user(self, utente_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM access_log WHERE utente_id = %s", (utente_id,))
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_by_user access_log: {e}")

    def read_by_file(self, file_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM access_log WHERE file_id = %s", (file_id,))
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_by_file access_log: {e}")

    def update(self, log_id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        keys = ', '.join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [log_id]
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE access_log SET {keys} WHERE id = %s RETURNING *", values)
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in update access_log: {e}")

    def delete(self, log_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM access_log WHERE id = %s", (log_id,))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in delete access_log: {e}")