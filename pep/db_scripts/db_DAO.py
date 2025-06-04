from db_scripts.db_operations import DatabaseManager

class FileDocumentoDAO:
    def __init__(self):
        db = DatabaseManager()
        self.conn = db.get_connection()
        self.cursor = db.get_cursor()

    def insert_file_documento(self, nome_file, contenuto, sensibilita):
        query = """
        INSERT INTO file_documenti (nome_file, contenuto, sensibilita)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        self.cursor.execute(query, (nome_file, contenuto, sensibilita))
        self.conn.commit()
        return self.cursor.fetchone()[0]  # fetchone()['id'] => fetchone()[0] per evitare errore

    def get_file_documento_by_id(self, file_id):
        query = "SELECT * FROM file_documenti WHERE id = %s;"
        self.cursor.execute(query, (file_id,))
        return self.cursor.fetchone()

    def update_file_documento(self, file_id, nome_file=None, contenuto=None, sensibilita=None):
        updates = []
        params = []

        if nome_file:
            updates.append("nome_file = %s")
            params.append(nome_file)
        if contenuto:
            updates.append("contenuto = %s")
            params.append(contenuto)
        if sensibilita:
            updates.append("sensibilita = %s")
            params.append(sensibilita)

        if not updates:
            return False

        params.append(file_id)
        query = f"UPDATE file_documenti SET {', '.join(updates)} WHERE id = %s;"
        self.cursor.execute(query, params)
        self.conn.commit()
        return True

    def delete_file_documento(self, file_id):
        self.cursor.execute("DELETE FROM file_documenti WHERE id = %s;", (file_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0