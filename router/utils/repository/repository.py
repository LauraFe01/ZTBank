from utils.database.connection import DatabaseConnection
from utils.database.config import DB_CONFIG
from utils.dao.user_dao import UserDAO
from utils.dao.utenti_ip_dao import UtentiIpDAO
from utils.dao.file_dao import FileDAO
from utils.dao.access_log_dao import AccessLogDAO
from utils.dao.network_trust_dao import NetworkTrustDAO

class Repository:
    """Repository centralizzato per accesso ai dati"""
    
    def __init__(self):
        self.db_connection = DatabaseConnection(DB_CONFIG)
        self._conn = None
        
    def _get_connection(self):
        """Ottiene connessione database"""
        if self._conn is None:
            self._conn = self.db_connection.connect()
        return self._conn

    @property
    def users(self) -> UserDAO:
        """Accesso al DAO utenti"""
        return UserDAO(self._get_connection())
    
    @property
    def user_ips(self) -> UtentiIpDAO:
        """Accesso al DAO utenti-IP"""
        return UtentiIpDAO(self._get_connection())
    
    @property
    def files(self) -> FileDAO:
        """Accesso al DAO file e documenti"""
        return FileDAO(self._get_connection())
    
    @property
    def access_logs(self) -> AccessLogDAO:
        """Accesso al DAO log degli accessi"""
        return AccessLogDAO(self._get_connection())
    
    @property
    def network_trust(self) -> NetworkTrustDAO:
        """Accesso al DAO network trust"""
        return NetworkTrustDAO(self._get_connection())
    
    def close(self):
        """Chiude connessione database"""
        if self.db_connection:
            self.db_connection.close()
