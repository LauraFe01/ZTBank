from db_scripts.db_DAO import FileDocumentoDAO
import logging

logging.basicConfig(level=logging.INFO)

def execute_single_operation(operation, doc_id, role):
    db_dao = FileDocumentoDAO()

    try:
        logging.info(f"[DB_EXEC] Operazione: {operation}, DocID: {doc_id}, Ruolo: {role}")
        if operation == "read":
            result = db_dao.get_file_documento_by_id(doc_id)
            if not result:
                logging.warning("[DB_EXEC] Documento non trovato")
                return None
            sensibilita = result[3]  # Assumendo che 'sensibilita' sia il 4° campo
            if sensibilita == 'sensibile' and role != "Direttore":
                logging.warning("[DB_EXEC] Accesso negato a documento sensibile per ruolo: %s", role)
                return None
            return result

        elif operation == "delete":
            deleted = db_dao.delete_file_documento(doc_id)
            logging.info(f"[DB_EXEC] Documento eliminato: {deleted}")
            return deleted

        else:
            logging.warning(f"[DB_EXEC] Operazione non valida: {operation}")
            return None

    except Exception as e:
        logging.error(f"[DB_EXEC] Errore: {e}")
        return None


def execute_write_operation(nome_file, contenuto, sensibilita):
    db_dao = FileDocumentoDAO()
    try:
        logging.info(f"[DB_EXEC] Inserimento file: {nome_file}")
        inserted_id = db_dao.insert_file_documento(nome_file, contenuto, sensibilita)
        logging.info(f"[DB_EXEC] Inserito con ID: {inserted_id}")
        return inserted_id
    except Exception as e:
        logging.error(f"[DB_EXEC] Errore: {e}")
        return False