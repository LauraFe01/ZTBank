from repository.irepository import IRepository
from dao.user_dao import UserDAO
from dao.utenti_ip_dao import UtentiIpDAO
from dao.file_dao import FileDAO
from dao.access_log_dao import AccessLogDAO

class Repository(IRepository):
    def __init__(self, conn):
        self.user_dao = UserDAO(conn)
        self.utenti_ip_dao = UtentiIpDAO(conn)
        self.file_dao = FileDAO(conn)
        self.access_log_dao = AccessLogDAO(conn)

    # User
    def get_user_by_id(self, user_id):
        return self.user_dao.read(user_id)
    def get_user_by_username(self, username):
        return self.user_dao.read_by_username(username)
    def get_all_users(self):
        return self.user_dao.read_all()
    def create_user(self, username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score):
        return self.user_dao.create(username, ruolo, codice_fiscale, indirizzo, email, telefono, trust_score)
    def update_user(self, user_id, **fields):
        return self.user_dao.update(user_id, **fields)
    def delete_user(self, user_id):
        self.user_dao.delete(user_id)

    # UtentiIp
    def get_ip_by_id(self, id):
        return self.utenti_ip_dao.read(id)
    def get_all_ips(self):
        return self.utenti_ip_dao.read_all()
    def get_ips_by_user(self, utente_id):
        return self.utenti_ip_dao.read_by_user(utente_id)
    def get_ips_by_ip(self, ip_address):
        return self.utenti_ip_dao.read_by_ip(ip_address)
    def create_ip(self, utente_id, ip_address, ip_ruolo):
        return self.utenti_ip_dao.create(utente_id, ip_address, ip_ruolo)
    def update_ip(self, id, **fields):
        return self.utenti_ip_dao.update(id, **fields)
    def delete_ip(self, id):
        self.utenti_ip_dao.delete(id)

    # File
    def get_file_by_id(self, file_id):
        return self.file_dao.read(file_id)
    def get_all_files(self):
        return self.file_dao.read_all()
    def get_files_by_user_id(self, user_id):
        return self.file_dao.read_by_owner(user_id)
    def create_file(self, nome_file, contenuto, sensibilita, proprietario_id):
        return self.file_dao.create(nome_file, contenuto, sensibilita, proprietario_id)
    def update_file(self, file_id, **fields):
        return self.file_dao.update(file_id, **fields)
    def delete_file(self, file_id):
        self.file_dao.delete(file_id)

    # AccessLog
    def get_log_by_id(self, log_id):
        return self.access_log_dao.read(log_id)
    def get_all_logs(self):
        return self.access_log_dao.read_all()
    def get_logs_by_user(self, user_id):
        return self.access_log_dao.read_by_user(user_id)
    def get_logs_by_file(self, file_id):
        return self.access_log_dao.read_by_file(file_id)
    def create_log(self, utente_id, file_id, azione, esito, motivazione):
        return self.access_log_dao.create(utente_id, file_id, azione, esito, motivazione)
    def update_log(self, log_id, **fields):
        return self.access_log_dao.update(log_id, **fields)
    def delete_log(self, log_id):
        self.access_log_dao.delete(log_id)