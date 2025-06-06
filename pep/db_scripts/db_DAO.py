from db_scripts.db_operations import DatabaseManager

class FileDocumentoDAO:
    """
    Data Access Object (DAO) per la gestione delle operazioni CRUD sulla tabella 'file_documenti'.

    Questa classe fornisce metodi per inserire, recuperare, aggiornare e cancellare record
    nella tabella 'file_documenti' del database. Utilizza il pattern Singleton per gestire
    la connessione al database tramite la classe DatabaseManager.
    """


    def __init__(self):
        """
        Inizializza la connessione al database e il cursore utilizzando DatabaseManager.
        """
        db = DatabaseManager()
        self.conn = db.get_connection()
        self.cursor = db.get_cursor()


    def insert_file_documento(self, nome_file, contenuto, sensibilita):
        """
        Inserisce un nuovo record nella tabella 'file_documenti'.

        Args:
            nome_file (str): Il nome del file.
            contenuto (bytes): Il contenuto binario del file.
            sensibilita (str): Il livello di sensibilità del documento.

        Returns:
            int: L'ID del record appena inserito.
        """
        query = """
        INSERT INTO file_documenti (nome_file, contenuto, sensibilita)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        self.cursor.execute(query, (nome_file, contenuto, sensibilita))
        self.conn.commit()
        return self.cursor.fetchone()[0]  # fetchone()['id'] => fetchone()[0] per evitare errore


    def get_file_documento_by_id(self, file_id):
        """
        Recupera un record dalla tabella 'file_documenti' utilizzando l'ID.

        Args:
            file_id (int): L'ID del file da recuperare.

        Returns:
            tuple or None: Una tupla contenente i dati del file se trovato, altrimenti None.
        """
        query = "SELECT * FROM file_documenti WHERE id = %s;"
        self.cursor.execute(query, (file_id,))
        return self.cursor.fetchone()


    def update_file_documento(self, file_id, nome_file=None, contenuto=None, sensibilita=None):
        """
        Aggiorna i campi specificati di un record nella tabella 'file_documenti'.

        Args:
            file_id (int): L'ID del file da aggiornare.
            nome_file (str, optional): Il nuovo nome del file.
            contenuto (bytes, optional): Il nuovo contenuto del file.
            sensibilita (str, optional): Il nuovo livello di sensibilità.

        Returns:
            bool: True se l'aggiornamento è avvenuto con successo, False altrimenti.
        """
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
        """
        Cancella un record dalla tabella 'file_documenti' utilizzando l'ID.

        Args:
            file_id (int): L'ID del file da cancellare.

        Returns:
            bool: True se il record è stato cancellato, False altrimenti.
        """
        self.cursor.execute("DELETE FROM file_documenti WHERE id = %s;", (file_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0