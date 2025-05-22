import psycopg2

class FileDAO:
    VALID_SENSIBILITA = {'sensibile', 'non_sensibile'}

    def __init__(self, conn):
        self.conn = conn

    def create(self, nome_file, contenuto, sensibilita, proprietario_id):
        # Validazione enum sensibilita
        if sensibilita not in self.VALID_SENSIBILITA:
            raise ValueError(f"Sensibilità non valida: {sensibilita}")
        # Validazione nome file
        if not nome_file:
            raise ValueError("Il nome del file è obbligatorio")
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO file_documenti (nome_file, contenuto, sensibilita, proprietario_id) VALUES (%s, %s, %s, %s) RETURNING *",
                    (nome_file, contenuto, sensibilita, proprietario_id)
                )
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in create file: {e}")

    def read(self, file_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM file_documenti WHERE id = %s", (file_id,))
                return cur.fetchone()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read file: {e}")

    def read_all(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM file_documenti")
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_all file: {e}")

    def read_by_owner(self, proprietario_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM file_documenti WHERE proprietario_id = %s", (proprietario_id,))
                return cur.fetchall()
        except psycopg2.Error as e:
            raise RuntimeError(f"Errore DB in read_by_owner file: {e}")

    def update(self, file_id, **fields):
        if not fields:
            raise ValueError("Nessun campo da aggiornare")
        keys = ', '.join(f"{k} = %s" for k in fields)
        values = list(fields.values()) + [file_id]
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"UPDATE file_documenti SET {keys} WHERE id = %s RETURNING *", values)
                self.conn.commit()
                return cur.fetchone()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in update file: {e}")

    def delete(self, file_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM file_documenti WHERE id = %s", (file_id,))
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise RuntimeError(f"Errore DB in delete file: {e}")