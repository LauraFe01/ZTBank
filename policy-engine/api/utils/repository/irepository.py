from abc import ABC, abstractmethod

class IRepository(ABC):
    # User
    @abstractmethod
    def get_user_by_id(self, user_id): pass
    @abstractmethod
    def get_user_by_username(self, username): pass
    @abstractmethod
    def get_all_users(self): pass
    @abstractmethod
    def create_user(self, username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score): pass
    @abstractmethod
    def update_user(self, user_id, **fields): pass
    @abstractmethod
    def delete_user(self, user_id): pass

    # UtentiIp
    @abstractmethod
    def get_ip_by_id(self, id): pass
    @abstractmethod
    def get_all_ips(self): pass
    @abstractmethod
    def get_ips_by_user(self, utente_id): pass
    @abstractmethod
    def get_ips_by_ip(self, ip_address): pass
    @abstractmethod
    def create_ip(self, utente_id, ip_address, ip_ruolo): pass
    @abstractmethod
    def update_ip(self, id, **fields): pass
    @abstractmethod
    def delete_ip(self, id): pass

    # File
    @abstractmethod
    def get_file_by_id(self, file_id): pass
    @abstractmethod
    def get_all_files(self): pass
    @abstractmethod
    def get_files_by_user_id(self, user_id): pass
    @abstractmethod
    def create_file(self, nome_file, contenuto, sensibilita, proprietario_id): pass
    @abstractmethod
    def update_file(self, file_id, **fields): pass
    @abstractmethod
    def delete_file(self, file_id): pass

    # AccessLog
    @abstractmethod
    def get_log_by_id(self, log_id): pass
    @abstractmethod
    def get_all_logs(self): pass
    @abstractmethod
    def get_logs_by_user(self, user_id): pass
    @abstractmethod
    def get_logs_by_file(self, file_id): pass
    @abstractmethod
    def create_log(self, utente_id, file_id, azione, esito, motivazione): pass
    @abstractmethod
    def update_log(self, log_id, **fields): pass
    @abstractmethod
    def delete_log(self, log_id): pass