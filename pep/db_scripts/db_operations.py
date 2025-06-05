import psycopg2
import os

class DatabaseManager:
    """
    Classe Singleton per la gestione della connessione al database PostgreSQL.

    Questa classe assicura che venga creata una sola istanza di connessione al database
    durante l'intero ciclo di vita dell'applicazione. È utile per evitare la creazione
    di connessioni multiple non necessarie, che potrebbero sovraccaricare il database.

    """
    _instance = None  # Attributo di classe per memorizzare l'istanza singleton
    _initialized = False  # Flag per verificare se l'istanza è già stata inizializzata


    def __new__(cls):
        """
        Metodo speciale per controllare la creazione dell'istanza.
        Se l'istanza non esiste, ne crea una nuova; altrimenti, restituisce quella esistente.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance


    def __init__(self):
        """
        Inizializza la connessione al database solo se non è già stata inizializzata.
        """
        if not self.__class__._initialized:
            self._init_connection()
            self.__class__._initialized = True


    def _init_connection(self):
        """
        Stabilisce la connessione al database utilizzando le variabili d'ambiente.
        """
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode='disable'
        )
        self.cursor = self.conn.cursor()


    def get_connection(self):
        """
        Restituisce l'oggetto connessione al database.
        """
        return self.conn


    def get_cursor(self):
        """
        Restituisce il cursore per eseguire le query sul database.
        """
        return self.cursor


    def close(self):
        """
        Chiude il cursore e la connessione al database.
        """
        self.cursor.close()
        self.conn.close()
